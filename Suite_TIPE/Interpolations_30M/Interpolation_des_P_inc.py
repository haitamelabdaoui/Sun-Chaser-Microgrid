import pandas as pd
from pathlib import Path

# --- GESTION DES CHEMINS ---
TIPE_DATA_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/TIPE_RESULT_36m2")
RESULT_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Interpolations_30M")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Chargement du fichier
fichier_pv = TIPE_DATA_DIR / 'puissance_incidante_finale_2024_36m2.csv'
df_pv = pd.read_csv(fichier_pv, sep=',', decimal='.')

# Renommage des colonnes si nécessaire
if 'datetime_formatee' in df_pv.columns:
    df_pv = df_pv.rename(columns={'datetime_formatee': 'date_time'})
if 'P_t_W_panneau_fixe' in df_pv.columns:
    df_pv = df_pv.rename(columns={
        'P_t_W_panneau_fixe': 'P_t_W_fixe', 
        'P_t_W_panneau_suiveur': 'P_t_W_suiveur'
    })

df_pv = df_pv.dropna(subset=['date_time']).copy() 

# --- CORRECTION CRITIQUE ICI : Ajouter dayfirst=True ---
df_pv['date_time'] = pd.to_datetime(df_pv['date_time'], dayfirst=True, errors='coerce')

if df_pv['date_time'].isna().any():
    print(f"Attention : {df_pv['date_time'].isna().sum()} lignes invalides ont été ignorées.")
    df_pv = df_pv.dropna(subset=['date_time'])

# Suppression des doublons d'horodatage
df_pv = df_pv.drop_duplicates(subset=['date_time'], keep='first')

# Indexation par la date
df_pv = df_pv.set_index('date_time')[['P_t_W_fixe', 'P_t_W_suiveur']]

for col in ['P_t_W_fixe', 'P_t_W_suiveur']:
    df_pv[col] = df_pv[col].astype(str).str.replace(',', '.').astype(float)

# Grille temporelle 30 min (17 568 pas)
index_30m = pd.date_range('2024-01-01 00:00', '2024-12-31 23:30', freq='30min', name='HORODATE')
df_30m = df_pv.reindex(index_30m).astype(float)

# Comblement du 01/01 si absent avec le 02/01
df_30m = df_30m.combine_first(df_30m.shift(-48))

# Interpolation linéaire sur les trous (1 pas de 30 min entre 2 mesures horaires)
df_30m = df_30m.interpolate(method='linear', limit=1).fillna(0).clip(lower=0)
df_30m = df_30m.astype(float)

# Conservation de l'énergie annuelle de référence
E_fixe = df_pv['P_t_W_fixe'].sum()
E_suiveur = df_pv['P_t_W_suiveur'].sum()

if (df_30m['P_t_W_fixe'] * 0.5).sum() > 0:
    df_30m['P_t_W_fixe'] *= (E_fixe / (df_30m['P_t_W_fixe'] * 0.5).sum())
if (df_30m['P_t_W_suiveur'] * 0.5).sum() > 0:
    df_30m['P_t_W_suiveur'] *= (E_suiveur / (df_30m['P_t_W_suiveur'] * 0.5).sum())

df_30m = df_30m[['P_t_W_fixe', 'P_t_W_suiveur']]
df_30m.index.name = 'HORODATE'

# Export du fichier corrigé
output_path = RESULT_DIR / 'TIPE_RESULT_30M.csv'
df_30m.to_csv(output_path, sep=';', decimal='.', date_format='%d/%m/%Y %H:%M:%S')

print(f"Fichier corrigé généré avec succès : {output_path}")