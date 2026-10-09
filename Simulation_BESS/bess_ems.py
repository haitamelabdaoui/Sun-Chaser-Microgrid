import numpy as np

# CAS 1 : Surplus de production (P_net > 0)

def traiter_cas_1_surplus(P_gen, P_load, SoC_curr, E_nom=10000, P_ch_max=5000, eta_ch=0.95, SoC_max=100, dt=0.5):
    """CAS 1 :P_net > 0
    - Si SoC < 100% : Charger la batterie en priorité avec le min(), puis injecter
    le surplus restant sur le réseau.
    - Si SoC = 100% : Batterie saturée, tout le surplus est injecté sur le
    réseau.
    """
    P_net = P_gen - P_load  # P_net > 0

    # Vérification de la capacité de la batterie
    if SoC_curr < SoC_max:
        # Puissance théorique nécessaire pour atteindre exactement SoC_max (100%) sur le pas dt
        P_needed_charge = ((SoC_max - SoC_curr) * E_nom) / (eta_ch * dt)
        P_ch = min(P_net, P_ch_max, P_needed_charge)
        # Convention : Charge -> P_batt < 0
        P_batt = -P_ch
        # Le reliquat non absorbé par la batterie est injecté sur le réseau (P_grid < 0)
        P_grid = -(P_net + P_batt)
    else:
        # Batterie déjà saturée à 100%
        P_batt = 0
        # L'intégralité du surplus net part sur le réseau régional
        P_grid = -P_net
    # Mise à jour de l'état de charge (SoC)
    P_ch_effective = -P_batt
    delta_SoC = (eta_ch * P_ch_effective / E_nom) * dt * 100.0
    SoC_next = min(SoC_max, SoC_curr + delta_SoC)
    return P_batt, P_grid, SoC_next


# CAS 2 : Déficit de production (P_net < 0)

def traiter_cas_2_deficit(P_gen, P_load, SoC_curr, E_nom=10000, P_dis_max=5000, eta_dis=0.95, SoC_min=10, dt=0.5):
    """CAS 2 : P_net < 0
    - Si SoC > 10% : Décharger la batterie en priorité avec le min(), puis
    compléter le déficit restant par l'achat sur le réseau.
    - Si SoC = 10% : Seuil critique de sécurité atteint, tout le déficit est acheté sur le réseau.
    """
    P_net = P_gen - P_load  # P_net < 0

    # Vérification de la capacité de la batterie
    if SoC_curr > SoC_min:
        # Puissance théorique nécessaire pour atteindre exactement SoC_min (10%) sur le pas dt
        P_available_discharge = (SoC_curr - SoC_min) * E_nom * eta_dis / dt
        P_dis = min(abs(P_net), P_dis_max, P_available_discharge)
        # Convention : Décharge -> P_batt > 0
        P_batt = P_dis
        # Le reliquat non couvert par la batterie est acheté sur le réseau (P_grid > 0)
        P_grid = abs(P_net) - P_batt
    else:
        # Batterie déjà saturée à 10%
        P_batt = 0
        # L'intégralité du déficit net est acheté sur le réseau régional
        P_grid = abs(P_net)
    # Mise à jour de l'état de charge (SoC)
    P_dis_effective = P_batt
    delta_SoC = -(P_dis_effective / (eta_dis * E_nom)) * dt * 100.0
    SoC_next = max(SoC_min, SoC_curr + delta_SoC)
    return P_batt, P_grid, SoC_next


# CAS 3 : Production égale à la consommation (P_net = 0)
def traiter_cas_3_equilibre(P_gen, P_load, SoC_curr):
    """CAS 3 : P_net = 0
    La production est égale à la consommation, il n'y a ni surplus ni déficit.
    La batterie reste inchangée et aucune énergie n'est échangée avec le réseau.
    """
    P_batt = 0
    P_grid = 0
    SoC_next = SoC_curr  # Pas de changement dans l'état de charge
    return P_batt, P_grid, SoC_next



#Cas 4 : Gestion en Heures Creuses

def calculer_soc_target(P_gen_prevus, P_load_prevus, E_nom=10000, dt=0.5, SoC_min=10):
    """fonction auxiliaire du Cas 4.
    Évalue le surplus solaire prévisionnel du lendemain et déduit la marge
    libre à réserver dans le BESS (SoC_target).
    """
    P_gen_prevus = np.array(P_gen_prevus)
    P_load_prevus = np.array(P_load_prevus)

    # 1. Calcul du surplus et du déficit prévisionnels (Wh)
    surplus_instantane = np.maximum(0, P_gen_prevus - P_load_prevus)
    delta_E_surplus = np.sum(surplus_instantane) * dt

    deficit_instantane = np.maximum(0, P_load_prevus - P_gen_prevus)
    delta_E_deficit = np.sum(deficit_instantane) * dt

    # le déficit ou surplus pris en compte ne peut pas dépasser E_nom (correction après execution)
    delta_E_deficit_eff = min(delta_E_deficit, E_nom)
    delta_E_surplus_eff = min(delta_E_surplus, E_nom)
    # On évalue l'énergie nette nécessaire pour la journée du lendemain (Déficit - Surplus)
    # Exprimée en pourcentage de la capacité nominale E_nom
    delta_E_net_pct = ((delta_E_deficit_eff - delta_E_surplus_eff) / E_nom) * 100.0

    # Si la journée est globalement déficitaire, on vise un SoC de sécurité 
    # égal au minimum vital + le besoin net, plafonné à 100%
    soc_target_brut = SoC_min

    if delta_E_net_pct > 0:
        soc_target_brut = SoC_min + delta_E_net_pct
    else:
        # Sinon (cas d'été), on réserve la marge libre pour le surplus 
        marge_libre_pct = (delta_E_surplus_eff / E_nom) * 100
        soc_target_brut = 100 - marge_libre_pct
        
    SoC_target = float(np.clip(soc_target_brut, SoC_min, 100)) #clip() pour s'assurer que SoC_target reste dans les limites de sécurité (SoC_min à 100%)
    #print(f"[DEBUG] Surplus prévu : {delta_E_surplus:.1f} Wh | Déficit prévu : {delta_E_deficit:.1f} Wh")
    #print(f"[DEBUG] Delta net (%) : {delta_E_net_pct:.1f}% -> SoC_target calculé : {SoC_target:.1f}%")
    return SoC_target, delta_E_surplus


def traiter_cas_4_offpeak(P_gen, P_load, SoC_curr, P_gen_prevus=None, P_load_prevus=None, SoC_target=None, E_nom=10000, P_ch_max=2000, P_grid_max_import=9000, eta_ch=0.95, eta_dis=0.95, SoC_min=10,SoC_max=100, dt=0.5):
    """CAS 4 : Gestion en Heures Creuses (Off-Peak Hours)
    Si SoC < SoC_target : La batterie se recharge depuis le réseau au tarif
    avantageux pour préparer la prochaine pointe. La puissance de charge est limitée par le min() 
    Si SoC >= SoC_target : Pas de recharge depuis le réseau.
    """
    # Appel de la sous-fonction si SoC_target doit être calculé dynamiquement
    if SoC_target is None:
        if P_gen_prevus is not None and P_load_prevus is not None:
            SoC_target, _ = calculer_soc_target(P_gen_prevus, P_load_prevus, E_nom=E_nom, dt=dt, SoC_min=SoC_min)
        else:
            # Valeur par défaut si aucune prévision n'est disponible (recharge à 100%)
            SoC_target = 100
    
    P_net = P_gen - P_load  # Généralement négatif ou nul en heures creuses (sauf exception en été, **remarque pertinente**)
    # Vérification si une recharge anticipée est nécessaire
    if P_net > 0: # correcton du code apres remarque: rise en compte de Pnet>0 exemple en été
        P_ch_max_soc = ((SoC_max - SoC_curr) / 100.0 * E_nom) / (eta_ch * dt)
        P_ch = min(P_net, P_ch_max, max(0.0, P_ch_max_soc))

        P_batt = -P_ch                  # Convention : Charge -> P_batt < 0
        P_grid = -P_net - P_batt
    else: 
         if SoC_curr < SoC_target:
            soc_a_gagner = SoC_target - SoC_curr
            # Énergie exacte nécessaire 
            E_needed = (soc_a_gagner / 100.0 * E_nom) / eta_ch
            # Puissance théorique nécessaire sur le pas de temps dt 
            P_needed_target = E_needed / dt
            # Terme 2 : Marge de puissance disponible sur l'abonnement réseau sans dépasser P_grid_max_import
            P_grid_available = max(0, P_grid_max_import + P_net) 
            # Application du min()
            P_ch = min(P_ch_max, P_needed_target, P_grid_available)
            # Convention : Charge -> P_batt < 0
            P_batt = -P_ch
            # Puissance totale soutirée au réseau (Alimentation de P_load + Recharge Batterie)
            P_grid = -P_net - P_batt  

         elif SoC_curr > SoC_target:
            P_def = max(0, -P_net) # Ce que demande la maison
            P_dispo_decharge = ((SoC_curr - SoC_target) / 100 * E_nom * eta_dis) / dt
            P_dis = min(P_def, P_ch_max, P_dispo_decharge) # On couvre la charge sans réinjecter
        
            P_batt = P_dis # Convention : Décharge -> P_batt > 0
            P_grid = -P_net - P_batt# Le réseau comble uniquement le reste

         else:
           # SoC cible déjà atteint : pas de charge supplémentaire depuis le réseau
           P_batt = 0
           # Le réseau couvre simplement le solde net de la maison
           P_grid = -P_net - P_batt

    # Mise à jour de l'état de charge (SoC)
    if P_batt < 0: # Cas Charge
        P_ch_effective = -P_batt
        delta_SoC = (eta_ch * P_ch_effective / E_nom) * dt * 100
        SoC_next = min(SoC_max, SoC_curr + delta_SoC)
    else: # Cas Décharge (ou inactif)
        P_dis_effective = P_batt
        delta_SoC = (P_dis_effective / (eta_dis * E_nom)) * dt * 100
        SoC_next = max(SoC_min, SoC_curr - delta_SoC)
    return P_batt, P_grid, SoC_next


####################################################################################

# Simulation BESS

def simuler_bess(df, E_nom=10000, SoC_init=50, dt=0.5):
    """
    Exécute la boucle de simulation BESS pour une colonne de production spécifique.
    """
    df_res = df.copy()    
    N = len(df_res)

    for mode in ['suiveur','fixe']:
        col_P_gen = f'P_gen_{mode}_W'
        res_P_batt = []
        res_P_grid = []
        res_SoC = []
        res_cas = []
        soc_curr = SoC_init
        
        for i in range(N):
            P_gen = df_res[col_P_gen].iloc[i] #iloc() pour accéder à la valeur de la colonne à l'index i
            P_load = df_res['P_load_W'].iloc[i]
            P_net = P_gen - P_load
            is_offpeak = df_res['is_offpeak'].iloc[i] 
            # Prévisions 24h pour le calcul du SoC Target
            P_gen_prevus = df_res[col_P_gen].iloc[i:i+48].values if i + 48 <= N else df_res[col_P_gen].iloc[i:].values # 48 pas de 30 min = 24h
            P_load_prevus = df_res['P_load_W'].iloc[i:i+48].values if i + 48 <= N else df_res['P_load_W'].iloc[i:].values
        
            if is_offpeak:
                P_batt, P_grid, SoC_next = traiter_cas_4_offpeak(P_gen, P_load, soc_curr, P_gen_prevus, P_load_prevus, E_nom=E_nom, dt=dt)
                cas = "Cas 4 (Heures Creuses)"
            elif P_net > 0: 
                P_batt, P_grid, SoC_next = traiter_cas_1_surplus(P_gen, P_load, soc_curr, E_nom=E_nom, dt=dt)
                cas = "Cas 1 (Surplus)"
            elif P_net < 0: 
                P_batt, P_grid, SoC_next = traiter_cas_2_deficit(P_gen, P_load, soc_curr, E_nom=E_nom, dt=dt)
                cas = "Cas 2 (Déficit)"
            else: 
                P_batt, P_grid, SoC_next = traiter_cas_3_equilibre(P_gen, P_load, soc_curr)
                cas = "Cas 3 (Équilibre)"     
            res_P_batt.append(P_batt)
            res_P_grid.append(P_grid)
            res_SoC.append(SoC_next)
            res_cas.append(cas)
            soc_curr = SoC_next

        df_res[f'P_gen_{mode}_W'] = df_res[col_P_gen]  
        df_res[f'P_load_W'] = df_res['P_load_W']  
        df_res[f'P_batt_{mode}'] = res_P_batt
        df_res[f'P_grid_{mode}'] = res_P_grid
        df_res[f'SoC_{mode}'] = res_SoC
        df_res[f'Cas_{mode}'] = res_cas
        
    return df_res