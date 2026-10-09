import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyse_financiere import (CAPEX_FIXE,CAPEX_SUIVEUR,OPEX_ANNUEL_FIXE,OPEX_ANNUEL_SUIVEUR,C_INJ,dt,compute_financial_kpis)

df = pd.read_csv('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Analyse_economique_financiere/simulation_BESS_annuelle_avec_prix.csv', sep=';')

df['HORODATE'] = pd.to_datetime(df['HORODATE'])
df.set_index('HORODATE', inplace=True)

col_ref = 'Cost_ref_€'
col_fixe = 'Cost_fixe_€'
col_suiveur = 'Cost_suiveur_€'

# Dépenses cumulées sur 365 jours
df['Cum_Cost_Ref'] = df[col_ref].cumsum()
df['Cum_Cost_Fixe'] = df[col_fixe].cumsum()
df['Cum_Cost_Suiveur'] = df[col_suiveur].cumsum()

# CALCUL DES TRAJECTOIRES FINANCIÈRES SUR 20 ANS

C_FIXE = 170
bill_ref = df[col_ref].sum() + C_FIXE
bill_fixe = df[col_fixe].sum() + C_FIXE
bill_suiveur = df[col_suiveur].sum() + C_FIXE

savings_fixe = bill_ref - bill_fixe
savings_suiveur = bill_ref - bill_suiveur

E_pv_fixe_kwh = (df['P_gen_fixe_W'] / 1000 * 0.5).sum()
E_pv_suiveur_kwh = (df['P_gen_suiveur_W'] / 1000 * 0.5).sum()


van_fixe, tri_fixe, pbp_fixe, lcoe_fixe, cum_cf_fixe = compute_financial_kpis(CAPEX_FIXE, OPEX_ANNUEL_FIXE, savings_fixe, E_pv_fixe_kwh)
van_suiveur, tri_suiveur, pbp_suiveur, lcoe_suiveur, cum_cf_suiveur = compute_financial_kpis(CAPEX_SUIVEUR, OPEX_ANNUEL_SUIVEUR, savings_suiveur, E_pv_suiveur_kwh)

years = np.arange(0, 21)

# CALCUL DES FLUX MENSUELS D'INJECTION (+) ET SOUTIRAGE (-)

# Séparation des flux (Soutirage > 0, Injection < 0)
df['Soutirage_Fixe_€'] = np.where(
    df['P_grid_fixe'] > 0, (df['P_grid_fixe'] / 1000) * dt * df['C_buy'], 0
)
df['Injection_Fixe_€'] = np.where(
    df['P_grid_fixe'] < 0, np.abs(df['P_grid_fixe'] / 1000) * dt * C_INJ, 0
)

df['Soutirage_Suiveur_€'] = np.where(
    df['P_grid_suiveur'] > 0, (df['P_grid_suiveur'] / 1000) * dt * df['C_buy'], 0
)
df['Injection_Suiveur_€'] = np.where(
    df['P_grid_suiveur'] < 0,
    np.abs(df['P_grid_suiveur'] / 1000) * dt * C_INJ,
    0,
)

# Agrégation par mois (Mois 1 à 12)
monthly = df.groupby(df.index.month).agg({
    'Soutirage_Fixe_€': 'sum',
    'Injection_Fixe_€': 'sum',
    'Soutirage_Suiveur_€': 'sum',
    'Injection_Suiveur_€': 'sum',
})

months_names = [
    'Jan',
    'Fév',
    'Mar',
    'Avr',
    'Mai',
    'Juin',
    'Juil',
    'Août',
    'Sep',
    'Oct',
    'Nov',
    'Déc',
]
x = np.arange(len(months_names))
width = 0.35  # Largeur des bâtonnets

# GRAPHIQUE A : Portefeuille Financier Cumulé (365 Jours)

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)

# PV Fixe (Bâtonnets décalés à gauche)
bars_inj_fixe = ax.bar(
    x - width / 2,
    monthly['Injection_Fixe_€'],
    width,
    label='Injection + (PV Fixe)',
    color='#f39c12',
    alpha=0.9,
)
bars_sout_fixe = ax.bar(
    x - width / 2,
    -monthly['Soutirage_Fixe_€'],
    width,
    label='Soutirage - (PV Fixe)',
    color="#0828f5",
    alpha=0.9,
)

# PV Suiveur (Bâtonnets décalés à droite)
bars_inj_suiv = ax.bar(
    x + width / 2,
    monthly['Injection_Suiveur_€'],
    width,
    label='Injection + (PV Suiveur)',
    color='#27ae60',
    alpha=0.9,
)
bars_sout_suiv = ax.bar(
    x + width / 2,
    -monthly['Soutirage_Suiveur_€'],
    width,
    label='Soutirage - (PV Suiveur)',
    color='#c0392b',
    alpha=0.9,
)


ax.bar_label(
    bars_inj_fixe,
    labels=[
        f'+{v:.1f} €' if v > 0.1 else '' for v in monthly['Injection_Fixe_€']
    ],
    padding=4,
    fontsize=7.5,
    fontweight='bold',
    rotation=90,
    color='#b9770e',
)
ax.bar_label(
    bars_sout_fixe,
    labels=[
        f'-{v:.1f} €' if v > 0.1 else '' for v in monthly['Soutirage_Fixe_€']
    ],
    padding=4,
    fontsize=7.5,
    fontweight='bold',
    rotation=90,
    color="#1945F5",
)
ax.bar_label(
    bars_inj_suiv,
    labels=[
        f'+{v:.1f} €' if v > 0.1 else '' for v in monthly['Injection_Suiveur_€']
    ],
    padding=4,
    fontsize=7.5,
    fontweight='bold',
    rotation=90,
    color='#1e8449',
)
ax.bar_label(
    bars_sout_suiv,
    labels=[
        f'-{v:.1f} €' if v > 0.1 else '' for v in monthly['Soutirage_Suiveur_€']
    ],
    padding=4,
    fontsize=7.5,
    fontweight='bold',
    rotation=90,
    color='#922b21',
)

# Ligne du zéro
ax.axhline(0, color='black', linewidth=1.2, linestyle='-')

# Habillage du graphique
ax.set_xticks(x)
ax.set_xticklabels(months_names, fontweight='bold', fontsize=10)
ax.set_ylabel(
    'Flux Financiers Mensuels (€)\n',
    fontsize=11,
    fontweight='bold',
)
ax.set_title(
    'Bilan Mensuel Dynamique : Gains d\'Injection vs Dépenses de Soutirage sur le Réseau (Mulhouse 2024)',
    fontsize=12,
    fontweight='bold',
    pad=14,
)
ax.grid(True, linestyle='--', alpha=0.4, color='gray')
ax.legend(loc='upper right', frameon=True, fontsize=9, ncol=2)

# Ajustement dynamique des marges Y pour laisser de la place aux textes
ymin, ymax = ax.get_ylim()
ax.set_ylim(ymin * 1.30, ymax * 1.35)

for spine in ax.spines.values():
  spine.set_linewidth(1.1)

plt.tight_layout()
plt.savefig('bilan_mensuel_injection_soutirage.png', dpi=300)
plt.close()

# GRAPHIQUE B : Cash-Flows Cumulés Actualisés sur 20 Ans

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)

# Tracé des courbes
ax.plot(
    years,
    cum_cf_fixe,
    marker='o',
    label='PV Fixe + BESS',
    color='#f39c12',
    linewidth=2,
    markersize=5,
)
ax.plot(
    years,
    cum_cf_suiveur,
    marker='s',
    label='PV Suiveur + BESS',
    color='#27ae60',
    linewidth=2.2,
    markersize=5,
)

# Seuil de rentabilité (VAN = 0)
ax.axhline(0, color='black', linewidth=1.1, linestyle='--')

# Repères verticaux pour le temps de retour (PBP)
ax.axvline(
    x=pbp_fixe, color='#f39c12', linestyle=':', linewidth=1.2, alpha=0.7
)
ax.axvline(
    x=pbp_suiveur, color='#27ae60', linestyle=':', linewidth=1.2, alpha=0.7
)

# Textes d'information sans flèches ni cadres (différenciation uniquement par la couleur)
ax.text(
    14.5,
    cum_cf_fixe[-1] - 2200,
    f'PBP Fixe: {pbp_fixe} ans\nVAN: {cum_cf_fixe[-1]:.2f} €',
    fontsize=9.5,
    fontweight='bold',
    color='#b9770e',
)

ax.text(
    14.5,
    cum_cf_suiveur[-1] + 1200,
    f'PBP Suiveur: {pbp_suiveur} ans\nVAN: {cum_cf_suiveur[-1]:.2f} €',
    fontsize=9.5,
    fontweight='bold',
    color='#1e8449',
)

# Habillage et marges du graphique
ax.set_ylim(-17000, 21000)
ax.set_xlabel("Année d'exploitation", fontsize=11, fontweight='bold')
ax.set_ylabel('Cash-Flow Cumulé Actualisé (€)', fontsize=11, fontweight='bold')
ax.set_title(
    'Trajectoire de Rentabilité Financière sur 20 Ans',
    fontsize=12,
    fontweight='bold',
    pad=12,
)
ax.set_xticks(years)
ax.grid(True, linestyle='--', alpha=0.4, color='gray')
ax.legend(loc='upper left', frameon=True, fontsize=10)

for spine in ax.spines.values():
  spine.set_linewidth(1.1)

plt.tight_layout()
plt.savefig('cash_flow_20years.png', dpi=300)
plt.close()

