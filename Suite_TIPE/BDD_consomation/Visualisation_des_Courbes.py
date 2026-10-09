from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd



# 2. Chargement des bases de données
df_gen = pd.read_csv("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Interpolations_30M/TIPE_SIMULATION_COMPLETE_30M.csv", sep=";",)
df_load = pd.read_csv("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/BDD_consomation/profil_consommation_2024.csv", sep=";",)

# 3. Conversion de la colonne temporelle HORODATE
df_gen["HORODATE"] = pd.to_datetime(
    df_gen["HORODATE"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
)
df_load["HORODATE"] = pd.to_datetime(df_load["HORODATE"], errors="coerce")

# 4. Fusion des deux BDD
df_merged = pd.merge(df_gen, df_load, on="HORODATE", how="inner")


# 5. Tracé du graphique
plt.figure(figsize=(15, 6), dpi=150)
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)

plt.plot(
    df_merged["HORODATE"],
    df_merged["P_gen_suiveur_W"],
    label="P_gen_suiveur_W",
    color="#27ae60",
    linewidth=1,
    alpha=0.85,
)
plt.plot(
    df_merged["HORODATE"],
    df_merged["P_gen_fixe_W"],
    label="P_gen_fixe_W",
    color="#2980b9",
    linewidth=1,
    alpha=0.85,
)
plt.plot(
    df_merged["HORODATE"],
    df_merged["P_load_W"],
    label="P_load_W",
    color="#e74c3c",
    linewidth=1,
    alpha=0.7,
)

plt.title(
    "Évolution temporelle de P_gen_suiveur_W, P_gen_fixe_W et P_load_W (2024)",
    fontsize=13,
    fontweight="bold",
)
plt.xlabel("Date", fontsize=11)
plt.ylabel("Puissance (W)", fontsize=11)
plt.legend(loc="upper right", frameon=True, fontsize=10)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()


# Sauvegarde et affichage
plt.savefig("/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/graphe_comparatif_suiveur_fixe_load.png", dpi=300)
plt.show()