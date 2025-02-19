import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# Fonction d'extraction des données EMG depuis la base de données
def EMG_game_extraction(ID_JOUEUR):
    try:
        connexion = sqlite3.connect("C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\Sleevy_App\instance\sleevy.db")
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Récupération du dernier session_id
        curseur.execute("SELECT DISTINCT session_id FROM sleevyemg WHERE idjoueur = ? ORDER BY session_id ASC;", (ID_JOUEUR,))
        session_ids = [row[0] for row in curseur.fetchall()]
        if not session_ids:
            print("Aucune session trouvée.")
            connexion.close()
            return {}
        dernier_session_id = session_ids[-1]
        
        # Récupération des valeurs EMG pour ce dernier session_id
        curseur.execute("SELECT valeuremg FROM sleevyemg WHERE idjoueur = ? AND session_id = ?;", (ID_JOUEUR, dernier_session_id))
        valeurs_emg = [row[0] for row in curseur.fetchall()]
        connexion.close()

        # Détection brutale des points
        points_brutaux = detection_brutale(valeurs_emg, group_size=70, seuil_diff=0.45)

        return {
            dernier_session_id: {
                "valeurs_emg": valeurs_emg,
                "points_brutaux": points_brutaux
            }
        }
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)
        return None


# Calcul du coefficient directeur (pente) d'une période de valeurs
def calculer_pente(valeurs):
    x = np.arange(len(valeurs))
    y = np.array(valeurs)
    pente = (y[-1] - y[0]) / (x[-1] - x[0])
    return pente


# Détection brutale en comparant des pentes entre deux périodes
def detection_brutale(valeurs_emg, group_size=50, seuil_diff=0.5):
    points = []
    moyenne_mobile = np.convolve(valeurs_emg, np.ones(group_size) / group_size, mode="valid")
    
    i = 0
    while i < len(moyenne_mobile) - 30:
        # Première période
        valeurs_premiere_periode = moyenne_mobile[i:i + 20]
        pente_premiere = calculer_pente(valeurs_premiere_periode)
        
        # Seconde période
        valeurs_seconde_periode = moyenne_mobile[i + 20:i + 40]
        pente_seconde = calculer_pente(valeurs_seconde_periode)
        
        # Comparaison des pentes
        if np.abs(pente_premiere - pente_seconde) < seuil_diff:
            i += 20
        else:
            points.append(i + 20)
            i += 20

    return points


# Fonction pour diviser la liste des valeurs EMG selon les points détectés
def diviser_par_points(valeurs_emg, points_brutaux):
    segments = []
    
    # Ajouter la première section avant le premier point rouge
    start_idx = 0
    for point in points_brutaux:
        segments.append(valeurs_emg[start_idx:point])
        start_idx = point
    
    # Ajouter la dernière section après le dernier point rouge
    segments.append(valeurs_emg[start_idx:])
    
    return segments


# Fonction pour afficher les résultats EMG, les pentes de chaque segment et les points détectés
def plot_emg_with_detections(valeurs_emg, points_brutaux, segments, group_size=40):
    plt.figure(figsize=(10, 6))
    
    # Tracer les valeurs EMG
    plt.plot(valeurs_emg, label="Valeurs EMG", color="b")
    
    # Calcul de la moyenne mobile
    moyenne_mobile = np.convolve(valeurs_emg, np.ones(group_size) / group_size, mode="valid")
    plt.plot(range(group_size - 1, len(valeurs_emg)), moyenne_mobile, label="Moyenne mobile", color="orange", linestyle='--')
    
    # Tracer les points de détection brutale
    plt.scatter(points_brutaux, [moyenne_mobile[i] for i in points_brutaux], color="red", label="Points Brutaux", zorder=5)
    
    # Calcul et affichage des pentes pour chaque segment sous forme de courbes
    start_idx = 0
    for i, point in enumerate(points_brutaux):
        segment = segments[i]
        pente = calculer_pente(segment)
        
        # Calculer les x et y pour la ligne droite représentant la pente
        x_vals = np.arange(start_idx, point)
        y_vals = np.array(segment) + pente * (x_vals - start_idx)  # Equation de la droite y = mx + b
        
        # Tracer la courbe correspondant à la pente de ce segment
        plt.plot(x_vals, y_vals, color="green", linestyle='--', label=f"Pente Segment {i+1}" if i == 0 else "")
        
        start_idx = point
    
    # Afficher la courbe pour le dernier segment
    last_segment = segments[-1]
    pente_last = calculer_pente(last_segment)
    last_x_vals = np.arange(start_idx, len(valeurs_emg))
    last_y_vals = np.array(last_segment) + pente_last * (last_x_vals - start_idx)
    plt.plot(last_x_vals, last_y_vals, color="green", linestyle='--', label=f"Pente Segment {len(segments)}")
    
    plt.title("Détection des moments de mort dans le jeu avec Pentes")
    plt.xlabel("Index")
    plt.ylabel("Valeur EMG")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()


# Fonction principale
def main():
    ID_JOUEUR = 1
    resultat = EMG_game_extraction(ID_JOUEUR)
    
    if resultat:
        session_id = list(resultat.keys())[0]
        valeurs_emg = resultat[session_id]["valeurs_emg"]
        points_brutaux = resultat[session_id]["points_brutaux"]
        
        # Diviser les valeurs EMG en segments avant et après chaque point rouge
        segments = diviser_par_points(valeurs_emg, points_brutaux)
        print("Segments divisés : ", len(segments))  # Affichez le nombre de segments
        
        # Affichage du graphique avec les pentes sous forme de courbes
        plot_emg_with_detections(valeurs_emg, points_brutaux, segments)

# Exécution du programme
if __name__ == "__main__":
    main()
