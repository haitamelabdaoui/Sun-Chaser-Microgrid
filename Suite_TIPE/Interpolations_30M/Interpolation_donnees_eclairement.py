import pandas as pd
from pathlib import Path

# --- GESTION DES CHEMINS ---
TIPE_DATA_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-TIPE/TIPE_GITHUB/BDD_CALC")
RESULT_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/TIPE_RESULT_36m2")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Chargement du fichier source depuis le dossier TIPE
fichier_eclairement = TIPE_DATA_DIR / 'BDD_eclairement_Mulhouse_2024.csv'
df_meteo = pd.read_csv(fichier_eclairement, sep=';', decimal=',')

df_meteo = df_meteo.dropna(subset=['date_time']).copy()
df_meteo['date_time'] = pd.to_datetime(df_meteo['date_time'], format='%d/%m/%Y %H:%M:%S')

# Sélection et placement de la date en INDEX
cols_meteo = ['Gb(i)', 'Gd(i)', 'Gr(i)', 'T2m(°C)', 'WS10m(m/s)']
df_meteo = df_meteo.set_index('date_time')[cols_meteo]

# Nettoyage des formats numériques (virgules en points)
for col in cols_meteo:
    df_meteo[col] = df_meteo[col].astype(str).str.replace(',', '.').astype(float)

# Création de la grille temporelle 30 min sur toute l'année 2024 (17 568 pas)
index_30m = pd.date_range('2024-01-01 00:00', '2024-12-31 23:30', freq='30min', name='HORODATE')
df_meteo_30m = df_meteo.reindex(index_30m).astype(float)

# Interpolation linéaire 
df_meteo_30m[['Gb(i)', 'Gd(i)', 'Gr(i)', 'WS10m(m/s)']] = (
    df_meteo_30m[['Gb(i)', 'Gd(i)', 'Gr(i)', 'WS10m(m/s)']]
    .interpolate(method='linear', limit=1)
    .fillna(0)
    .clip(lower=0)
)

# Température : interpolation linéaire sans limite inférieure (autorise les valeurs négatives en hiver)
df_meteo_30m[['T2m(°C)']] = (
    df_meteo_30m[['T2m(°C)']]
    .interpolate(method='linear', limit=1)
    .bfill()
    .ffill()
)

df_meteo_30m = df_meteo_30m.astype(float)
df_meteo_30m.index.name = 'HORODATE'

# Export du fichier dans le dossier de résultats du microgrid
output_path = RESULT_DIR / 'BDD_eclairement_Mulhouse_30M.csv'
df_meteo_30m.to_csv(output_path, sep=';', decimal='.', date_format='%d/%m/%Y %H:%M:%S')

print(f"Fichier météo 30 min généré avec succès : {output_path}")