# data_loader.py
import pandas as pd

def charger_donnees(data_load="/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/BDD_consomation/profil_consommation_2024.csv", 
                                data_gen="/Users/haitamelabdaoui/Desktop/Sun-Chaser/Sun-Chaser-Microgrids/Interpolations_30M/TIPE_SIMULATION_COMPLETE_30M.csv"):
    """
    Extrait les variables utiles des deux BDD et construit un tableau de bord propre pour la simulation.
    """
    # Lecture des BDD
    df_load = pd.read_csv(data_load, sep=';')
    df_gen = pd.read_csv(data_gen, sep=';')
    
    # Extraction et assemblage des colonnes 
    df = pd.DataFrame({'HORODATE': pd.to_datetime(df_load['HORODATE'], format='%Y-%m-%d %H:%M:%S'),
                       'P_load_W': df_load['P_load_W'],
                       'P_gen_suiveur_W': df_gen['P_gen_suiveur_W'],
                       'P_gen_fixe_W': df_gen['P_gen_fixe_W']})
    
    # Identification des Heures Creuses (22h à 6h)
    heures = df['HORODATE'].dt.hour 
    df['is_offpeak'] = heures.isin([22, 23, 0, 1, 2, 3, 4, 5]) #isin() pour vérifier si l'heure est dans le créneau Heures Creuses
    return df