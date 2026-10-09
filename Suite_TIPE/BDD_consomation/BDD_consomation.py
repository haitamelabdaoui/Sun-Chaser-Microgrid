from pathlib import Path
import pandas as pd

# 1. Gestion dynamique du chemin du fichier CSV
DOSSIER_SCRIPT = Path(__file__).resolve().parent
fichier_entree = DOSSIER_SCRIPT / "coefficients-des-profils.csv"
fichier_sortie = DOSSIER_SCRIPT / "profil_consommation_2024.csv"

# 2. Chargement des données brutes
df = pd.read_csv(fichier_entree, sep=";")

# 3. Conversion du texte ISO en datetime (conservation de l'heure locale)
df["HORODATE"] = pd.to_datetime(df["HORODATE"].str[:19])

# 4. Rééchantillonnage explicite de 30 min (Moyenne des coefficients)
df_30min = (
    df.groupby(["SOUS_PROFIL", "CATEGORIE"])
    .resample("30min", on="HORODATE")[
        ["COEFFICIENT_PREPARE", "COEFFICIENT_AJUSTE"]
    ]
    .mean()
    .reset_index()
)

# 5. Séparation des sous-profils au pas de 30 min
df_semaine = df_30min[df_30min["SOUS_PROFIL"] == "RES11WE_SEM"].copy()
df_weekend = df_30min[df_30min["SOUS_PROFIL"] == "RES11WE_WE"].copy()

# 6. Élimination des doublons potentiels sur l'horodate
df_semaine = df_semaine.groupby("HORODATE", as_index=False)[
    ["COEFFICIENT_PREPARE", "COEFFICIENT_AJUSTE"]
].mean()

df_weekend = df_weekend.groupby("HORODATE", as_index=False)[
    ["COEFFICIENT_PREPARE", "COEFFICIENT_AJUSTE"]
].mean()

# 7. Fusion des deux sous-profils sur la même grille temporelle de 30 min
df_final = pd.merge(
    df_semaine, df_weekend, on="HORODATE", suffixes=("_SEM", "_WE")
)

# 8. Reconstitution des coefficients globaux
df_final["COEFFICIENT_PREPARE"] = (
    df_final["COEFFICIENT_PREPARE_SEM"] + df_final["COEFFICIENT_PREPARE_WE"]
)
df_final["COEFFICIENT_AJUSTE"] = (
    df_final["COEFFICIENT_AJUSTE_SEM"] + df_final["COEFFICIENT_AJUSTE_WE"]
)

df_final["SOUS_PROFIL"] = "RES11WE"
df_final["CATEGORIE"] = "RES11"

# 9. Mise à l'échelle pour une énergie annuelle totale de 9 000 kWh
energie_annuelle_kWh = 9000
somme_totale_coefs = df_final["COEFFICIENT_AJUSTE"].sum()

# Facteur d'échelle pour la puissance instantanée en kW (pas dt = 0.5 h)
F_echelle_kW = energie_annuelle_kWh / (0.5 * somme_totale_coefs)

# Puissance moyenne instantanée (kW et W)
df_final["P_load_KW"] = df_final["COEFFICIENT_AJUSTE"] * F_echelle_kW
df_final["P_load_W"] = df_final["P_load_KW"] * 1000

# Énergie consommée par pas de 30 min (kWh) : E_i = P_kW * 0.5 h
df_final["E_KWH"] = df_final["P_load_KW"] * 0.5

# 10. Reformatage de l'horodate au format lisible YYYY-MM-DD HH:MM:SS
df_final["HORODATE"] = df_final["HORODATE"].dt.strftime("%Y-%m-%d %H:%M:%S")

# 11. Sauvegarde propre
colonnes_export = [
    "HORODATE",
    "SOUS_PROFIL",
    "CATEGORIE",
    "COEFFICIENT_PREPARE",
    "COEFFICIENT_AJUSTE",
    "P_load_W",
]

tableau_export = df_final[colonnes_export]
tableau_export.to_csv(fichier_sortie, index=False, sep=";")

# Vérifications dans la console
print(f"Facteur d'échelle puissance (kW) : {F_echelle_kW:.6f}")
print(
    f"Somme directe de la colonne E_KWH : {df_final['E_KWH'].sum():.2f} kWh"
)
print(
    f"Somme de la colonne P_load_W : {df_final['P_load_W'].sum():.2f} W"
)