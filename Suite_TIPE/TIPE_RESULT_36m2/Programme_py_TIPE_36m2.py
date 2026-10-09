import pandas as pd 
import numpy as np 
from pathlib import Path

# --- GESTION DES CHEMINS ---
# 1. Dossier source des fichiers CSV mathématiques du TIPE
TIPE_DATA_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-TIPE/TIPE_GITHUB/BDD_CALC")

# 2. Dossier de destination pour les résultats du microgrid (36 m²)
RESULT_DIR = Path("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/TIPE_RESULT_36m2")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

def verifier_colonnes(df, colonnes_attendues, nom_fichier):
    colonnes_manquantes = [col for col in colonnes_attendues if col not in df.columns]
    if colonnes_manquantes:
        raise KeyError(
            f"Colonnes manquantes dans {nom_fichier}: {colonnes_manquantes}"
        )

def vecteur_panneau(alpha_deg, beta_deg):
    alpha = np.radians(alpha_deg)
    beta = np.radians(beta_deg)
    return np.array([
        np.sin(beta) * np.sin(alpha),
        np.sin(beta) * np.cos(alpha),
        np.cos(beta),
    ])

def chercher_orientation_suiveur_max(ligne, alphas, betas, surface):
    meilleur_resultat = None

    for alpha_deg in alphas:
        for beta_deg in betas:
            up = vecteur_panneau(alpha_deg, beta_deg)
            dot = (
                ligne["Us_x"] * up[0]
                + ligne["Us_y"] * up[1]
                + ligne["Us_z"] * up[2]
            )
            puissance = ligne["E_W_m2"] * surface * max(0, dot)

            if meilleur_resultat is None or puissance > meilleur_resultat["P_t_W_suiveur"]:
                meilleur_resultat = {
                    "date_time": ligne["date_time"],
                    "alpha_suiveur_deg": alpha_deg,
                    "beta_suiveur_deg": beta_deg,
                    "dot_product_suiveur": dot,
                    "P_t_W_suiveur": puissance,
                }

    return meilleur_resultat


# --- CHARGEMENT DES FICHIERS CSV ---
fichier_us = TIPE_DATA_DIR / "BDD_VecteurUs_Mulhouse_2024.csv"
fichier_eclairement = TIPE_DATA_DIR / "BDD_eclairement_Mulhouse_2024.csv"

# Lecture correcte des CSV au format français (séparateur point-virgule)
df_us = pd.read_csv(fichier_us, sep=';', decimal=',')
df_eclairement = pd.read_csv(fichier_eclairement, sep=';', decimal=',')

verifier_colonnes(df_us, ["date_time", "Us_x", "Us_y", "Us_z"], fichier_us.name)
verifier_colonnes(df_eclairement, ["date_time", "Gb(i)", "Gd(i)", "Gr(i)"], fichier_eclairement.name)

df_eclairement["E_W_m2"] = (
    df_eclairement["Gb(i)"] + df_eclairement["Gd(i)"] + df_eclairement["Gr(i)"]
)

# Fusionner les vecteurs solaires avec l'éclairement
df = df_us.merge(
    df_eclairement[["date_time", "E_W_m2"]],
    on="date_time",
    how="left",
)
df = df.dropna(subset=["E_W_m2"]).copy()

# --- PARAMÈTRES DU MICROGRID (36 m²) ---
alpha_fixe_deg = 180
beta_fixe_deg = 45
surface = 36.0  # Surface totale du toit

Up = vecteur_panneau(alpha_fixe_deg, beta_fixe_deg)

# Calcul de la puissance instantanée (Toit fixe)
df["dot_product"] = df["Us_x"] * Up[0] + df["Us_y"] * Up[1] + df["Us_z"] * Up[2]
df["P_t_W"] = df["E_W_m2"] * surface * np.maximum(0, df["dot_product"])

# Export de la puissance du panneau fixe (36m²)
df.to_csv(RESULT_DIR / "puissance_incidante_36m2.csv", index=False)

# Grille de recherche alpha-beta pour le suiveur
alphas = np.arange(0, 181, 5)
betas = np.arange(0, 91, 5)

print("Calcul de l'optimisation du suiveur pour 36m² en cours...")
resultats_suiveur = []

for _, ligne in df.iterrows():
    resultat_suiveur = chercher_orientation_suiveur_max(
        ligne,
        alphas,
        betas,
        surface,
    )
    resultats_suiveur.append(resultat_suiveur)

df_suiveur = pd.DataFrame(resultats_suiveur)

# Fusion des résultats du suiveur
df = df.merge(df_suiveur, on="date_time", how="left")

df["P_t_W_panneau_fixe"] = df["P_t_W"]
df["P_t_W_panneau_suiveur"] = df["P_t_W_suiveur"]

colonnes_finales = [
    "date_time",
    "elevation_deg",
    "azimuth_deg",
    "elevation_rad",
    "azimuth_rad",
    "Us_x",
    "Us_y",
    "Us_z",
    "E_W_m2",
    "dot_product",
    "dot_product_suiveur",
    "alpha_suiveur_deg",
    "beta_suiveur_deg",
    "P_t_W_panneau_fixe",
    "P_t_W_panneau_suiveur",
]

df_final = df[colonnes_finales].rename(columns={"date_time": "datetime_formatee"})
df_final.to_csv(RESULT_DIR / "puissance_incidante_finale_2024_36m2.csv", index=False)

# --- BILAN ÉNERGÉTIQUE ANNUEL ---
energie_totale_fixe = df["P_t_W"].sum() * 1e-3  
energie_totale_suiveur = df["P_t_W_suiveur"].sum() * 1e-3
gain_wh = energie_totale_suiveur - energie_totale_fixe
gain_pourcent = (gain_wh / energie_totale_fixe) * 100 

comparaison_energies = pd.DataFrame([
    {
        "energie_totale_fixe_Wh": energie_totale_fixe,
        "energie_totale_suiveur_Wh": energie_totale_suiveur,
        "gain_suiveur_Wh": gain_wh,
        "gain_suiveur_pourcent": gain_pourcent
    }
])



print(f"Energie totale panneau fixe : {energie_totale_fixe:.2f} kWh")
print(f"Energie totale panneau suiveur : {energie_totale_suiveur:.2f} kWh")
print(f"Gain énergétique : {gain_pourcent:.2f}%")