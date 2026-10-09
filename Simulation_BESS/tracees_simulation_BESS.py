import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd


df = pd.read_csv('simulation_BESS_annuelle.csv', sep=';')
df['HORODATE'] = pd.to_datetime(df['HORODATE'])
df.set_index('HORODATE', inplace=True)

#GRAPHIQUE 1 : Comparaison Fixe vs Suiveur (Bilan annuel)
modes = [('fixe', '(a) Système PV Fixe'), ('suiveur', '(b) Système PV Suiveur')]

colors = {
    'P_Grid_net': '#0096ff',
    'P_PV_net': '#80c4ff',
    'P_Batt_dch': '#a040ff',
    'P_Load': '#00c000',
    'P_Batt_ch': '#f5b025',
    'P_Grid_exp': '#d00000',
}

x = np.arange(12)
months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
]
bar_width = 0.35

# Calcul préalable de l'amplitude globale minimale et maximale sur l'ensemble des deux modes
max_pos_global = 0
min_neg_global = 0

monthly_dfs = {}
for mode, title in modes:
  gen = df[f'P_gen_{mode}_W']
  load = df['P_load_W']
  batt = df[f'P_batt_{mode}']
  grid = df[f'P_grid_{mode}']

  df_mode = pd.DataFrame(index=df.index)
  df_mode['P_grid_net'] = np.maximum(grid, 0)
  df_mode['P_pv_net'] = np.maximum(gen, 0)
  df_mode['P_batt_dch'] = np.maximum(batt, 0)
  df_mode['P_load_neg'] = -load
  df_mode['P_batt_ch'] = np.minimum(batt, 0)
  df_mode['P_grid_exp'] = np.minimum(grid, 0)

  monthly_df = df_mode.groupby(df_mode.index.month)[
      [
          'P_grid_net',
          'P_pv_net',
          'P_batt_dch',
          'P_load_neg',
          'P_batt_ch',
          'P_grid_exp',
      ]
  ].mean()
  monthly_dfs[mode] = monthly_df

  pos_height = (
      monthly_df['P_grid_net']
      + monthly_df['P_pv_net']
      + monthly_df['P_batt_dch']
  )
  neg_height = (
      monthly_df['P_load_neg']
      + monthly_df['P_batt_ch']
      + monthly_df['P_grid_exp']
  )

  max_pos_global = max(max_pos_global, pos_height.max())
  min_neg_global = min(min_neg_global, neg_height.min())

# Marge verticale uniforme pour les deux subplots
ylim_min = min_neg_global * 1.10
ylim_max = max_pos_global * 1.45

# Création des 2 subplots partageant le même axe y
fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300, sharey=True)

for ax, (mode, title) in zip(axes, modes):
  monthly_df = monthly_dfs[mode]

  # Empilement positif (Offre)
  bottom_pos = np.zeros(12)
  ax.bar(
      x,
      monthly_df['P_grid_net'],
      bottom=bottom_pos,
      width=bar_width,
      color=colors['P_Grid_net'],
      label=r'$P_{\mathrm{Grid,net}}$',
  )
  bottom_pos += monthly_df['P_grid_net']

  ax.bar(
      x,
      monthly_df['P_pv_net'],
      bottom=bottom_pos,
      width=bar_width,
      color=colors['P_PV_net'],
      label=r'$P_{\mathrm{PV,net}}$',
  )
  bottom_pos += monthly_df['P_pv_net']

  ax.bar(
      x,
      monthly_df['P_batt_dch'],
      bottom=bottom_pos,
      width=bar_width,
      color=colors['P_Batt_dch'],
      label=r'$P_{\mathrm{Batt,dch}}$',
  )
  bottom_pos += monthly_df['P_batt_dch']

  # Empilement négatif (Demande)
  bottom_neg = np.zeros(12)
  ax.bar(
      x,
      monthly_df['P_load_neg'],
      bottom=bottom_neg,
      width=bar_width,
      color=colors['P_Load'],
      label=r'$P_{\mathrm{Load}}$',
  )
  bottom_neg += monthly_df['P_load_neg']

  ax.bar(
      x,
      monthly_df['P_batt_ch'],
      bottom=bottom_neg,
      width=bar_width,
      color=colors['P_Batt_ch'],
      label=r'$P_{\mathrm{Batt,ch}}$',
  )
  bottom_neg += monthly_df['P_batt_ch']

  ax.bar(
      x,
      monthly_df['P_grid_exp'],
      bottom=bottom_neg,
      width=bar_width,
      color=colors['P_Grid_exp'],
      label=r'$P_{\mathrm{Grid,exp}}$',
  )
  bottom_neg += monthly_df['P_grid_exp']

  # Application des mêmes limites Y aux deux subplots
  ax.set_ylim(ylim_min, ylim_max)

  ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
  ax.set_xlabel('Mois', fontsize=12, fontweight='bold', labelpad=8)

  ax.set_xticks(x)
  ax.set_xticklabels(months, fontsize=11)
  ax.tick_params(axis='y', labelsize=11)

  ax.tick_params(
      direction='in',
      top=True,
      right=True,
      left=True,
      bottom=True,
      length=6,
      width=1,
  )
  for spine in ax.spines.values():
    spine.set_linewidth(1.2)
    spine.set_color('black')

  ax.legend(
      loc='upper right',
      ncol=2,
      frameon=False,
      fontsize=10,
      handletextpad=0.3,
      columnspacing=0.8,
  )

axes[0].set_ylabel(
    'Puissance moyenne offre/demande (W)',
    fontsize=12,
    fontweight='bold',
    labelpad=8,
)


plt.tight_layout()
plt.savefig('BESS_fixe_suiveur.png', dpi=300)
plt.show()


# GRAPHIQUE 2 : Semaine d'été type (1-7 Juillet)

summer_slice = df.loc['2024-07-01':'2024-07-07']

fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Puissances PV & Charge
axes[0].plot(summer_slice.index, summer_slice['P_gen_suiveur_W'], label='PV Suiveur', color='orange', alpha=0.9)
axes[0].plot(summer_slice.index, summer_slice['P_gen_fixe_W'], label='PV Fixe', color='gold', alpha=0.8, linestyle='--')
axes[0].plot(summer_slice.index, summer_slice['P_load_W'], label='Charge', color="#BF0E0E", alpha=0.9)
axes[0].set_ylabel('Puissance (W)')
axes[0].set_title("Semaine d'été type (1-7 Juillet) : Production PV vs Charge", fontweight='bold')
axes[0].legend(loc='upper right')

# Puissance Batterie
axes[1].plot(summer_slice.index, summer_slice['P_batt_suiveur'], label='P_batt (Suiveur)', color='blue', alpha=0.8)
axes[1].plot(summer_slice.index, summer_slice['P_batt_fixe'], label='P_batt (Fixe)', color='deepskyblue', alpha=0.6, linestyle='--')
axes[1].set_ylabel('Puissance Batterie (W)')
axes[1].set_title('Puissance Batterie (+ Charge, - Décharge)')
axes[1].legend(loc='upper right')

# État de charge (SoC)
axes[2].plot(summer_slice.index, summer_slice['SoC_suiveur'], label='SoC Suiveur', color='green', alpha=0.8)
axes[2].plot(summer_slice.index, summer_slice['SoC_fixe'], label='SoC Fixe', color='limegreen', alpha=0.6, linestyle='--')
axes[2].set_ylabel('SoC (%)')
axes[2].set_xlabel('Date')
axes[2].set_title('État de charge (SoC) de la batterie')
axes[2].legend(loc='upper right')

plt.tight_layout()
plt.savefig('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Simulation_BESS/summer_week_analysis.png', dpi=300)
plt.close()



# GRAPHIQUE 3 : Semaine d'hiver type (10-17 Janvier)

print("Génération du graphique 3 (Semaine d'hiver)...")
winter_slice = df.loc['2024-01-10':'2024-01-17']

fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Puissances PV & Charge
axes[0].plot(winter_slice.index, winter_slice['P_gen_suiveur_W'], label='PV Suiveur', color='orange')
axes[0].plot(winter_slice.index, winter_slice['P_gen_fixe_W'], label='PV Fixe', color='gold', linestyle='--')
axes[0].plot(winter_slice.index, winter_slice['P_load_W'], label='Charge', color="#BF0E0E")
axes[0].set_ylabel('Puissance (W)')
axes[0].set_title("Semaine d'hiver type (10-17 Janvier) : Production PV vs Charge", fontweight='bold')
axes[0].legend(loc='upper right')

# Puissance Batterie
axes[1].plot(winter_slice.index, winter_slice['P_batt_suiveur'], label='P_batt (Suiveur)', color='blue')
axes[1].plot(winter_slice.index, winter_slice['P_batt_fixe'], label='P_batt (Fixe)', color='deepskyblue', linestyle='--')
axes[1].set_ylabel('Puissance Batterie (W)')
axes[1].legend(loc='upper right')

# État de charge (SoC)
axes[2].plot(winter_slice.index, winter_slice['SoC_suiveur'], label='SoC Suiveur', color='green')
axes[2].plot(winter_slice.index, winter_slice['SoC_fixe'], label='SoC Fixe', color='limegreen', linestyle='--')
axes[2].set_ylabel('SoC (%)')
axes[2].set_xlabel('Date')
axes[2].legend(loc='upper right')

plt.tight_layout()
plt.savefig('/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Simulation_BESS/winter_week_analysis.png', dpi=300)
plt.close()

print("Tous les graphiques ont été générés et enregistrés avec succès !")

#GRAPHIQUE 4: Profils horaires annuels

df['Hour'] = df.index.hour + df.index.minute / 60.0
df['Month'] = df.index.month

# 2. Calcul des moyennes par heure pour chaque saison
summer_avg = df[df['Month'].isin([6, 7, 8])].groupby('Hour').mean(numeric_only=True)
winter_avg = df[df['Month'].isin([12, 1, 2])].groupby('Hour').mean(numeric_only=True)

# Charte graphique
COLORS = {
    'PV_suiveur': '#d35400',   # Orange foncé
    'PV_fixe': '#f39c12',      # Or / Jaune
    'Charge': '#2c3e50',       # Anthracite / Slate
    'Batt_suiveur': '#8e44ad', # Violet
    'Batt_fixe': '#2980b9',   # Bleu
    'SoC_suiveur': '#27ae60',  # Vert
    'SoC_fixe': '#2ecc71',     # Vert clair
}

# 3. Création des figures (3 lignes x 2 colonnes)
fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True, dpi=300)

seasons_data = [
    (summer_avg, "Moyenne Estivale (Juin - Août)", 0),
    (winter_avg, "Moyenne Hivernale (Déc - Fév)", 1)
]

for avg_df, season_title, col in seasons_data:
    # --- Sous-graphique 1 : PV & Charge ---
    ax0 = axes[0, col]
    ax0.plot(avg_df.index, avg_df['P_gen_suiveur_W'], label='PV Suiveur', color=COLORS['PV_suiveur'], linewidth=2)
    ax0.plot(avg_df.index, avg_df['P_gen_fixe_W'], label='PV Fixe', color=COLORS['PV_fixe'], linestyle='--', linewidth=2)
    ax0.plot(avg_df.index, avg_df['P_load_W'], label='Charge', color=COLORS['Charge'], linewidth=1.5, alpha=0.85)
    ax0.set_title(season_title, fontsize=12, fontweight='bold', pad=10)
    if col == 0:
        ax0.set_ylabel('Puissance (W)', fontsize=11, fontweight='bold')
    max_val = max(avg_df['P_gen_suiveur_W'].max(), avg_df['P_load_W'].max())
    ax0.set_ylim(-100, max_val * 1.25)
    ax0.legend(loc='upper right', frameon=False, fontsize=9.5)

    # --- Sous-graphique 2 : Puissance Batterie ---
    ax1 = axes[1, col]
    ax1.plot(avg_df.index, avg_df['P_batt_suiveur'], label='P_batt (Suiveur)', color=COLORS['Batt_suiveur'], linewidth=2)
    ax1.plot(avg_df.index, avg_df['P_batt_fixe'], label='P_batt (Fixe)', color=COLORS['Batt_fixe'], linestyle='--', linewidth=2)
    ax1.axhline(0, color='black', linewidth=0.8, linestyle=':', alpha=0.7)
    if col == 0:
        ax1.set_ylabel('Puissance BESS (W)', fontsize=11, fontweight='bold')
    min_b = min(avg_df['P_batt_suiveur'].min(), avg_df['P_batt_fixe'].min())
    max_b = max(avg_df['P_batt_suiveur'].max(), avg_df['P_batt_fixe'].max())
    ax1.set_ylim(min_b * 1.25, max(max_b * 1.45, 800))
    ax1.legend(loc='upper right', frameon=False, fontsize=9.5)

    # --- Sous-graphique 3 : État de Charge (SoC) ---
    ax2 = axes[2, col]
    ax2.plot(avg_df.index, avg_df['SoC_suiveur'], label='SoC Suiveur', color=COLORS['SoC_suiveur'], linewidth=2)
    ax2.plot(avg_df.index, avg_df['SoC_fixe'], label='SoC Fixe', color=COLORS['SoC_fixe'], linestyle='--', linewidth=2)
    if col == 0:
        ax2.set_ylabel('SoC (%)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Heure de la journée (h)', fontsize=11, fontweight='bold', labelpad=6)
    ax2.set_ylim(0, 115)
    ax2.set_xlim(0, 24)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(4))
    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax2.legend(loc='upper right', frameon=False, fontsize=9.5)

# Style global des axes
for ax in axes.flat:
    ax.tick_params(direction='in', top=True, right=True, left=True, bottom=True, length=5, width=1, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.35, color='gray')
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color('black')

fig.suptitle("Profils Moyens Journaliers (0h - 24h) : Été vs Hiver", fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.savefig('daily_profiles_summer_winter.png', dpi=300)
plt.close()

print("Graphique 1 enregistré : daily_profiles_summer_winter.png")

# GRAPHIQUE 5 : Répartition des Modes de Gestion EMS


# Tri et étiquettes
cases_order = ['Cas 1 (Surplus)', 'Cas 2 (Déficit)', 'Cas 4 (Heures Creuses)']
labels_short = [
    'Cas 1 : Surplus PV\n(P_gen > P_load)', 
    'Cas 2 : Déficit PV\n(P_gen < P_load)', 
    'Cas 4 : Heures Creuses\n(Recharge réseau)'
]

# Conversions en heures (1 pas = 0.5 h)
s_hours = [df['Cas_suiveur'].value_counts()[c] * 0.5 for c in cases_order]
f_hours = [df['Cas_fixe'].value_counts()[c] * 0.5 for c in cases_order]

s_pct = [df['Cas_suiveur'].value_counts(normalize=True)[c] * 100 for c in cases_order]
f_pct = [df['Cas_fixe'].value_counts(normalize=True)[c] * 100 for c in cases_order]

x = np.arange(len(cases_order))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

rects1 = ax.bar(x - width/2, s_hours, width, label='PV Suiveur + BESS', color='#d35400', alpha=0.9, edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x + width/2, f_hours, width, label='PV Fixe + BESS', color='#f39c12', alpha=0.85, edgecolor='black', linewidth=0.8)

ax.set_ylabel('Nombre d\'heures cumulées dans l\'année (h)', fontsize=11, fontweight='bold')
ax.set_title('Comparaison de la Répartition des Modes de Gestion EMS (2024)', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(labels_short, fontsize=10.5, fontweight='bold')
ax.legend(loc='upper right', frameon=False, fontsize=10.5)

ax.grid(True, linestyle='--', alpha=0.35, axis='y', color='gray')
ax.set_ylim(0, 4200)

# Valeurs au-dessus des barres
for rect, pct in zip(rects1, s_pct):
    height = rect.get_height()
    ax.annotate(f'{height:.0f} h\n({pct:.1f}%)',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 4), textcoords="offset points",
                ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#8c2d00')

for rect, pct in zip(rects2, f_pct):
    height = rect.get_height()
    ax.annotate(f'{height:.0f} h\n({pct:.1f}%)',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 4), textcoords="offset points",
                ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#a36200')

# Badges synthétiques d'écart
diff_surplus = s_hours[0] - f_hours[0]
ax.annotate(f'+{diff_surplus:.0f} h d\'autonomie (+13.4%)', xy=(0, max(s_hours[0], f_hours[0]) + 350),
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle="round,pad=0.3", fc="#e8f8f5", ec="#27ae60", lw=1.2))

diff_deficit = s_hours[1] - f_hours[1]
ax.annotate(f'{diff_deficit:.0f} h de déficit (-8.6%)', xy=(1, max(s_hours[1], f_hours[1]) + 350),
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle="round,pad=0.3", fc="#fadbd8", ec="#c0392b", lw=1.2))

for spine in ax.spines.values():
    spine.set_linewidth(1.1)
    spine.set_color('black')

plt.tight_layout()
plt.savefig('ems_modes_barchart.png', dpi=300)
plt.close()

print("Graphique 6 (Bâtons) enregistré : ems_modes_barchart.png")

