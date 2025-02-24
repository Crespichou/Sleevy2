import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

ID_JOUEUR = 1  # Argument

def ACCEL_game_extraction():  # Pas de limite de points
    try:
        # Connexion à la base de données
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\Sleevy_App\instance\sleevy.db")
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Récupérer tous les session_id distincts pour le joueur
        requete_session_ids = """
        SELECT DISTINCT session_id
        FROM sleevyaccelerometre
        WHERE idjoueur = ?
        ORDER BY session_id ASC;
        """
        curseur.execute(requete_session_ids, (ID_JOUEUR,))
        session_ids = [row[0] for row in curseur.fetchall()]
        
        if not session_ids:
            print("Aucune session trouvée.")
            connexion.close()
            return {}

        session_data = {}  # Dictionnaire pour stocker les données

        for session_id in session_ids:
            # Récupération des valeurs d'accélération et de l'heure pour chaque session
            requete_valeurs = """
            SELECT valeuraccel, heureaccel
            FROM sleevyaccelerometre
            WHERE idjoueur = ? AND session_id = ?
            ORDER BY heureaccel ASC;
            """
            
            curseur.execute(requete_valeurs, (ID_JOUEUR, session_id))
            result = curseur.fetchall()
            
            if result:
                valeurs_accel = [row[0] for row in result]  # Liste des valeurs d'accélération
                heures_accel = [row[1] for row in result]  # Liste des heures d'accélération

                # Convertir heureaccel en format HH:MM:SS.sss
                heures_accel = [datetime.strptime(heure, "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S.%f")[:-4] for heure in heures_accel]
                
                session_data[session_id] = (heures_accel, valeurs_accel)  # Stockage des heures et des valeurs d'accélération

        connexion.close()
        return session_data  # Retourne les données
    
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)
        return None

def plot_accel_data(interval=100):  # Ajouter un intervalle pour choisir le nombre de points à afficher
    data = ACCEL_game_extraction()
    if not data:
        print("Aucune donnée à afficher.")
        return
    
    plt.figure(figsize=(12, 6))  # Taille de la figure
    
    for session_id, (heures, valeurs) in data.items():
        plt.plot(heures, valeurs, label=f"Session {session_id}")
        
        # Affichage des labels d'heures tous les `interval` échantillons
        plt.xticks(np.arange(0, len(heures), interval), heures[::interval], rotation=45)
    
    plt.xlabel("Heure d'accélération")
    plt.ylabel("Valeur d'accélération")
    plt.title("Évolution des valeurs d'accélération par session")
    plt.legend()
    plt.grid(True)  # Ajouter une grille pour une meilleure lisibilité
    plt.tight_layout()  # Ajuster les marges du graphique
    plt.show()

plot_accel_data(interval=700)  # Par exemple, afficher un label tous les 100 points
