import pandas as pd

df_pv = pd.read_csv('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Interpolations_30M/TIPE_RESULT_30M.csv', sep=';', decimal='.')
df_meteo = pd.read_csv('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Interpolations_30M/BDD_eclairement_Mulhouse_30M.csv', sep=';', decimal='.')

# Conversion et placement de l'index temporel
df_pv['HORODATE'] = pd.to_datetime(df_pv['HORODATE'], format='%d/%m/%Y %H:%M:%S')
df_pv = df_pv.set_index('HORODATE')

df_meteo['HORODATE'] = pd.to_datetime(df_meteo['HORODATE'], format='%d/%m/%Y %H:%M:%S')
df_meteo = df_meteo.set_index('HORODATE')

# Jointure des deux bases sur l'index temporel 
df_merged = df_pv.join(df_meteo, how='inner') #inner join pour ne conserver que les mesures communs aux deux bases

# 3. Paramètres du système PV et du modèle thermique de Faiman

eta_STC = 0.2111      # Rendement sous conditions STC
A_pv = 36          # Surface couverte en panneau (m^2)
T_STC = 25            # Température de référence (°C)
gamma = -0.0035       # Coefficient de température de Pmax (%/°C)
f_fixe = 0.9129       # Facteur de pertes fixes
U0_prime = 25.0       # Paramètre thermique de Faiman 
U1_prime = 6.84       # Paramètre thermique de Faiman (sensibilité au vent)

# Calculs pour le système FIXE
df_merged['G_inc_fixe'] = df_merged['P_t_W_fixe'] / A_pv
df_merged['T_cell_fixe'] = df_merged['T2m(°C)'] + (df_merged['G_inc_fixe'] / (U0_prime + U1_prime * df_merged['WS10m(m/s)']))
df_merged['PR_fixe'] = (1 + gamma * (df_merged['T_cell_fixe'] - T_STC)) * f_fixe
df_merged['P_gen_fixe_W'] = eta_STC * df_merged['PR_fixe'] * df_merged['P_t_W_fixe']

# Calculs pour le système SUIVEUR 
df_merged['G_inc_suiveur'] = df_merged['P_t_W_suiveur'] / A_pv
df_merged['T_cell_suiveur'] = df_merged['T2m(°C)'] + (df_merged['G_inc_suiveur'] / (U0_prime + U1_prime * df_merged['WS10m(m/s)']))
df_merged['PR_suiveur'] = (1 + gamma * (df_merged['T_cell_suiveur'] - T_STC)) * f_fixe
df_merged['P_gen_suiveur_W'] = eta_STC * df_merged['PR_suiveur'] * df_merged['P_t_W_suiveur']

# 6. Calcul de l'énergie annuelle (pas de 30 min = 0.5 heure)
energie_fixe_30m = (df_merged['P_gen_fixe_W'] * 0.5).sum() * 1e-3     
energie_suiveur_30m = (df_merged['P_gen_suiveur_W'] * 0.5).sum() * 1e-3
gain_30m = ((energie_suiveur_30m - energie_fixe_30m) / energie_fixe_30m) * 100 

# Rendement annuel effectif moyen
eta_annuel_fixe = (df_merged['P_gen_fixe_W'].sum() / df_merged['P_t_W_fixe'].sum()) * 100
eta_annuel_suiveur = (df_merged['P_gen_suiveur_W'].sum() / df_merged['P_t_W_suiveur'].sum()) * 100

print(f"Énergie annuelle FIXE (30min)    : {energie_fixe_30m:.2f} kWh")
print(f"Énergie annuelle SUIVEUR (30min) : {energie_suiveur_30m:.2f} kWh")
print(f"Gain énergétique du tracking     : +{gain_30m:.2f} %")
print(f"Rendement annuel FIXE            : {eta_annuel_fixe:.2f} %")
print(f"Rendement annuel SUIVEUR         : {eta_annuel_suiveur:.2f} %")

df_merged.to_csv('TIPE_SIMULATION_COMPLETE_30M.csv', sep=';', decimal='.', date_format='%d/%m/%Y %H:%M:%S')
