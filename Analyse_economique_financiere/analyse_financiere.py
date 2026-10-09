import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf


df = pd.read_csv('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Simulation_BESS/simulation_BESS_annuelle.csv', sep=';')
df['HORODATE'] = pd.to_datetime(df['HORODATE'])
df.set_index('HORODATE', inplace=True)

dt = 0.5  

#  Paramètres tarifaires (EDF 2024)
C_HP = 0.2700    # Tarif Achat Heures Pleines (€/kWh) - 06h à 22h
C_HC = 0.2068    # Tarif Achat Heures Creuses (€/kWh) - 22h à 06h
C_INJ = 0.1301   # Tarif Revente Surplus EDF OA (€/kWh)
C_FIXE = 170   # Abonnement annuel réseau (€/an)

# Identification des plages horaires (HC: 22h-06h, HP: 06h-22h)
df['Hour_num'] = df.index.hour
df['Is_HC'] = (df['Hour_num'] >= 22) | (df['Hour_num'] < 6)
df['C_buy'] = np.where(df['Is_HC'], C_HC, C_HP) #np.where pour appliquer le tarif HC ou HP selon l'heure
#  Cas de Référence (Sans PV ni Batterie)
df['Cost_ref_€'] = (df['P_load_W'] / 1000) * dt * df['C_buy']
bill_ref = df['Cost_ref_€'].sum() + C_FIXE

# B. Cas PV Fixe + BESS
P_grid_fixe_kW = df['P_grid_fixe'] / 1000
df['Cost_fixe_€'] = np.where(P_grid_fixe_kW > 0,
                             P_grid_fixe_kW * dt * df['C_buy'],        # Achat réseau
                             P_grid_fixe_kW * dt * C_INJ)              # Vente surplus 
bill_fixe = df['Cost_fixe_€'].sum() + C_FIXE

# C. Cas PV Suiveur + BESS
P_grid_suiveur_kW = df['P_grid_suiveur'] / 1000
df['Cost_suiveur_€'] = np.where(
    P_grid_suiveur_kW > 0,
    P_grid_suiveur_kW * dt * df['C_buy'],     # Achat réseau
    P_grid_suiveur_kW * dt * C_INJ)           # Vente surplus

bill_suiveur = df['Cost_suiveur_€'].sum() + C_FIXE

df.to_csv('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Analyse_economique_financiere/simulation_BESS_annuelle_avec_prix.csv', sep=';')

# Économies annuelles réalisées 
savings_fixe_2024 = bill_ref - bill_fixe
savings_suiveur_2024 = bill_ref - bill_suiveur

# Production annuelle
E_pv_fixe_kwh = (df['P_gen_fixe_W'] / 1000 * dt).sum()
E_pv_suiveur_kwh = (df['P_gen_suiveur_W'] / 1000 * dt).sum()

# HYPOTHÈSES DE CAPEX & OPEX (SYSTÈME DOMESTIQUE)

# Caractéristiques physiques du champ PV 
S_totale = 36          # Surface totale(m²)
S_panneau = 1.80          # Surface d'un module (m²)
P_module_stc = 380    # Puissance crête d'un module (Wc)

N_panneaux = S_totale / S_panneau  # 20 panneaux
P_kWc = (N_panneaux * P_module_stc) / 1000  # 7.6 kWc

#  coûts d'investissement (CAPEX en Euros)
capex_pv_modules = N_panneaux * 120    # 2 400 € (20 modules de 380 Wc)
capex_onduleur_8kw = 1900             # Onduleur hybride 8 kW compatible LUNA2000
capex_bess_luna10k = 5800           # Huawei LUNA2000-10-S0 (10 kWh)
capex_cables = 800         # Protection câblage
capex_iot = 300            # Contrôleur IoT, ESP32, capteurs
capex_structure_fixe = 700         # Ancrage fixe

# Surcoût mécanique du suiveur 2 axes pour 36 m² (Moteurs, vérins, châssis)
capex_surcout_tracker = 3200     

# Totaux CAPEX
CAPEX_FIXE = (capex_pv_modules + capex_onduleur_8kw + capex_bess_luna10k + capex_cables + capex_iot + capex_structure_fixe)
# Total Fixe = 11 900 €

CAPEX_SUIVEUR = (capex_pv_modules + capex_onduleur_8kw + capex_bess_luna10k + capex_cables + capex_iot + capex_structure_fixe + capex_surcout_tracker)
# Total Suiveur = 14 400 €

# OPEX annuels révisés (Maintenance proportionnelle à la taille du système)
OPEX_ANNUEL_FIXE = 120   # Maintenance préventive et contrôle (1% du CAPEX hors BESS)
OPEX_ANNUEL_SUIVEUR = 180 # Maintenance préventive + graissage/vérification mécanique suiveur


# 5. PROJECTION FINANCIÈRE SUR 20 ANS (VAN, TRI, LCOE)

def compute_financial_kpis(
    capex,
    opex_annuel,
    savings_y1,
    E_pv_y1,
    r_e=0.03,  # Taux d'inflation annuel de l'électricité (3.0%)
    d=0.04,  # Taux d'actualisation financier (4.0%)
    N_years=20,  # Durée d'évaluation du projet (20 ans)
    delta=0.005,  # Taux de dégradation annuel du PV (0.5%/an)
    extra_maint_year10=1000,  # Remplacement onduleur à l'année 10 (1000 €)
):
  """Calcule les KPIs financiers (VAN, TRI, PBP, LCOE) pour le microréseau."""
  cash_flows = [-capex]
  pv_production = []  # Production effective année par année

  for y in range(1, N_years + 1):
    # Économie brute actualisée à l'inflation de l'électricité
    sav_y = savings_y1 * ((1 + r_e) ** (y - 1))

    # CapEx de réinvestissement exceptionnel à l'année 10
    extra_maint = extra_maint_year10 if y == 10 else 0

    # Flux de trésorerie net annuel (NCF_y)
    ncf = sav_y - (opex_annuel + extra_maint)
    cash_flows.append(ncf)

    # Production PV ajustée de la dégradation linéaire
    E_pv_y = E_pv_y1 * ((1 - delta) ** (y - 1))
    pv_production.append(E_pv_y)

  # Valeur Actuelle Nette (NPV)
  npv = npf.npv(d, cash_flows) 

  # Taux de Rendement Interne (TRI / IRR)
  irr = npf.irr(cash_flows) * 100

  # Temps de Retour sur Investissement Actualisé (PBP)
  cum_cf = np.cumsum([cash_flows[0] / ((1 + d) ** 0)] + [cf / ((1 + d) ** i) for i, cf in enumerate(cash_flows[1:], 1)])
  pbp = int(np.argmax(cum_cf >= 0)) if np.any(cum_cf >= 0) else N_years #np.argmax pour trouver l'année où le cumul devient positif, sinon retourne N_years si jamais il ne devient pas positif

  # 4. Coût Égalisé de l'Énergie (LCOE) avec dégradation intégrée
  discounted_costs = capex + sum([(opex_annuel + extra_maint) / ((1 + d) ** y) for y in range(1, N_years + 1)])
  discounted_energy = sum([E_pv_y / ((1 + d) ** y)for y in range(1, N_years + 1)])
  lcoe = discounted_costs / discounted_energy

  return npv, irr, pbp, lcoe, cum_cf


# EXECUTION DES CALCULS (FIXE VS SUIVEUR)

van_fixe, tri_fixe, pbp_fixe, lcoe_fixe, cum_cf_fixe = compute_financial_kpis(CAPEX_FIXE, OPEX_ANNUEL_FIXE, savings_fixe_2024, E_pv_fixe_kwh)
van_suiveur, tri_suiveur, pbp_suiveur, lcoe_suiveur, cum_cf_suiveur = compute_financial_kpis(CAPEX_SUIVEUR, OPEX_ANNUEL_SUIVEUR, savings_suiveur_2024, E_pv_suiveur_kwh)

# SYNTHÈSE DES RÉSULTATS


print("BILAN ÉCONOMIQUE et FINANCIER DU MICRORÉSEAU DOMESTIQUE")

print(f"Facture Annuelle de Référence (Sans PV) : {bill_ref:10.2f} €/an")

print("INDICATEURS FINANCIERS                PV FIXE + BESS     PV SUIVEUR + BESS")

print(f"Facture Annuelle Optimisée:           {bill_fixe:10.2f} €/an "               f"  {bill_suiveur:10.2f} €/an")
print(f"Économie Annuelle (Année 2024):       {savings_fixe_2024:10.2f} €/an "       f"  {savings_suiveur_2024:10.2f} €/an")
print(f"CAPEX:                                {CAPEX_FIXE:10.2f} €   "               f"  {CAPEX_SUIVEUR:10.2f} €")
print(f"OPEX (1%):                            {OPEX_ANNUEL_FIXE:10.2f} €/an "        f"  {OPEX_ANNUEL_SUIVEUR:10.2f} €/an")

print(f"LCOE:                                 {lcoe_fixe:10.4f} €/kWh "              f"  {lcoe_suiveur:10.4f} €/kWh")
print(f"VAN:                                  {van_fixe:10.2f} €   "                 f"  {van_suiveur:10.2f} €")
print(f"TRI:                                  {tri_fixe:10.2f} %     "               f"  {tri_suiveur:10.2f} %")
print(f"PBP:                                  {pbp_fixe:10d} ans   "                 f"  {pbp_suiveur:10d} ans")
