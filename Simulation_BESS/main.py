# main.py
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from data_loader import charger_donnees
from bess_ems import simuler_bess


# Chargement des données
df = charger_donnees()
# Exécution de la simulation BESS 
df_sim = simuler_bess(df, E_nom=10000, SoC_init=50, dt=0.5)
dt = 0.5
E_load = df_sim['P_load_W'].sum() * dt / 1000 #E_load c'est la consommation totale en kWh sur la période de simulation

# Suiveur
E_gen_suiv = df_sim['P_gen_suiveur_W'].sum() * dt / 1000 # E_gen_suiv c'est la production totale en kWh sur la période de simulation
E_inj_suiv = np.maximum(0, -df_sim['P_grid_suiveur']).sum() * dt / 1000 # E_inj_suiv c'est l'énergie injectée sur le réseau en kWh sur la période de simulation
E_sout_suiv = np.maximum(0, df_sim['P_grid_suiveur']).sum() * dt / 1000 # E_sout_suiv c'est l'énergie soutirée du réseau en kWh sur la période de simulation
Tx_auto_suiv = ((E_load - E_sout_suiv) / E_load) * 100.0 # Tx_auto_suiv c'est le taux d'autonomie en % sur la période de simulation

# Fixe
E_gen_fixe = df_sim['P_gen_fixe_W'].sum() * dt / 1000
E_inj_fixe = np.maximum(0, -df_sim['P_grid_fixe']).sum() * dt / 1000
E_sout_fixe = np.maximum(0, df_sim['P_grid_fixe']).sum() * dt / 1000 
Tx_auto_fixe = ((E_load - E_sout_fixe) / E_load) * 100 

# 4. Bilan dans la console
print("BILAN COMPARATIF BESS : FIXE vs SUIVEUR ")
print(f"Production Solaire : Fixe = {E_gen_fixe:.1f} kWh | Suiveur = {E_gen_suiv:.1f} kWh | Écart = {((E_gen_suiv - E_gen_fixe) / E_gen_fixe) * 100:+.1f}%")
print(f"Achat Réseau       : Fixe = {E_sout_fixe:.1f} kWh | Suiveur = {E_sout_suiv:.1f} kWh | Écart = {((E_sout_suiv - E_sout_fixe) / E_sout_fixe) * 100:+.1f}%")
print(f"Vente Réseau       : Fixe = {E_inj_fixe:.1f} kWh | Suiveur = {E_inj_suiv:.1f} kWh | Écart = {((E_inj_suiv - E_inj_fixe) / E_inj_fixe) * 100:+.1f}%")
print(f"Taux d'Autonomie   : Fixe = {Tx_auto_fixe:.1f}%     | Suiveur = {Tx_auto_suiv:.1f}%     | Écart = {Tx_auto_suiv - Tx_auto_fixe:+.1f}%")

# Sélection des colonnes à exporter (optionnel mais propre)
colonnes_export = ['HORODATE', 'P_gen_suiveur_W','P_gen_fixe_W', 'P_load_W','P_batt_suiveur', 'P_batt_fixe','P_grid_suiveur', 'P_grid_fixe','SoC_suiveur', 'SoC_fixe','Cas_suiveur', 'Cas_fixe']

# Export direct vers un fichier CSV
df_sim[colonnes_export].to_csv('simulation_BESS_annuelle.csv', sep=';',)


