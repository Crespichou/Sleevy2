import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Configuration des méthodes à activer/désactiver
ACTIVER_DETECTION_OUTLIERS_ECART_TYPE = False #Pas terrible mais peut marcher
ACTIVER_DETECTION_OUTLIERS_IQR = False #Nulle 
ACTIVER_DETECTION_POINTS_MORTS = False #Bien 
ACTIVER_DETECTION_ANTOINE = True #La meilleure mais joueur avec seuil
ACTIVER_ISOLATION_FOREST = False #Nulle
ACTIVER_DETECTION_OUTLIERS_CUSTOM = False #Nulle

def EMG_game_extraction(ID_JOUEUR):
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db")  # Lien tablette Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Requête pour récupérer tous les session_id distincts associés à idjoueur = 1, triés par ordre croissant
        requete_session_ids = """
        SELECT DISTINCT session_id
        FROM sleevyemg
        WHERE idjoueur = ?
        ORDER BY session_id ASC;
        """
        
        curseur.execute(requete_session_ids, (ID_JOUEUR,))
        session_ids = [row[0] for row in curseur.fetchall()]
        
        if not session_ids:
            print("Aucune session trouvée.")
            connexion.close()
            return {}
        
        # Prendre le dernier session_id
        dernier_session_id = session_ids[-1]
        
        # Récupération des valeurs EMG pour ce dernier session_id
        requete_valeurs = """
        SELECT valeuremg
        FROM sleevyemg 
        WHERE idjoueur = ? AND session_id = ?;
        """
    
        curseur.execute(requete_valeurs, (ID_JOUEUR, dernier_session_id,))
        result = curseur.fetchall()  # Récupère toutes les valeurs sous forme de liste de tuples

        valeurs_emg = [row[0] for row in result]  # Convertit en liste simple
        
        outliers_ecart_type, outliers_iqr, dead_points, antoine_points, outliers_custom, outliers_if = [], [], [], [], [], []
        
        # Détection des outliers si activée
        if ACTIVER_DETECTION_OUTLIERS_ECART_TYPE:
            outliers_ecart_type, _ = detect_outliers(valeurs_emg)
        
        if ACTIVER_DETECTION_OUTLIERS_IQR:
            _, outliers_iqr = detect_outliers(valeurs_emg)
        
        if ACTIVER_DETECTION_POINTS_MORTS:
            dead_points = detect_dead_points(valeurs_emg, seuil=20)
        
        if ACTIVER_DETECTION_ANTOINE:
            antoine_points = antoine(valeurs_emg)
        
        if ACTIVER_ISOLATION_FOREST:
            outliers_if = detect_outliers_isolation_forest(valeurs_emg)
        
        if ACTIVER_DETECTION_OUTLIERS_CUSTOM:
            outliers_custom = detect_outliers_custom(valeurs_emg)
        
        print(f"Points morts détectés : {dead_points}")
        print(f"Points antoine détectés : {antoine_points}")
        print(f"Outliers (écart-type) détectés : {outliers_ecart_type}")
        print(f"Outliers (IQR) détectés : {outliers_iqr}")
        print(f"Outliers (Isolation Forest) détectés : {outliers_if}")
        print(f"Outliers (custom) détectés : {outliers_custom}")
        
        connexion.close()
        return {
            dernier_session_id: {
                "valeurs_emg": valeurs_emg,
                "outliers_ecart_type": outliers_ecart_type,
                "outliers_iqr": outliers_iqr,
                "dead_points": dead_points,
                "antoine_points": antoine_points,
                "outliers_custom": outliers_custom,
                "outliers_if": outliers_if
            }
        }  # Retourne les données avec les résultats activés
    
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)
        return None

# Méthode de détection des outliers par écart-type et IQR
def detect_outliers(valeurs_emg):
    """Détecte les valeurs aberrantes (outliers) dans les données EMG."""
    valeurs_emg = np.array(valeurs_emg)

    # Méthode 1 : Détection basée sur l'écart-type
    mean = np.mean(valeurs_emg)
    std_dev = np.std(valeurs_emg)
    seuil_ecart_type = 1.4  # Définit un seuil à 2 écarts-types (modifiable)
    
    outliers_ecart_type = []
    for i, valeur in enumerate(valeurs_emg):
        if abs(valeur - mean) > seuil_ecart_type * std_dev:
            outliers_ecart_type.append(i)  # Index de l'outlier

    # Méthode 2 : Détection basée sur l'IQR
    Q1 = np.percentile(valeurs_emg, 25)
    Q3 = np.percentile(valeurs_emg, 75)
    IQR = Q3 - Q1
    seuil_iqr_bas = Q1 - 1.5 * IQR
    seuil_iqr_haut = Q3 + 1.5 * IQR
    
    outliers_iqr = []
    for i, valeur in enumerate(valeurs_emg):
        if valeur < seuil_iqr_bas or valeur > seuil_iqr_haut:
            outliers_iqr.append(i)  # Index de l'outlier

    return outliers_ecart_type, outliers_iqr

# Détection des points morts
def detect_dead_points(valeurs_emg, seuil=50):
    """Détecte les points où il y a un changement significatif dans les données EMG."""
    differences = np.diff(valeurs_emg)
    dead_points = np.where(np.abs(differences) > seuil)[0]  # Indices des changements brusques
    return dead_points

# Méthode Antoine
def antoine(valeurs_emg, group_size=40, compare_size=10, seuil_diff=0.2):
    points_antoine = []
    for i in range(len(valeurs_emg) - group_size - compare_size):
        moyenne_mobile = np.mean(valeurs_emg[i:i + group_size])
        comparaison = np.mean(valeurs_emg[i + group_size:i + group_size + compare_size])
        if abs(moyenne_mobile - comparaison) > seuil_diff * moyenne_mobile:
            points_antoine.append(i + group_size)  # Ajouter l'indice du point
    return points_antoine

# Détection des outliers custom (exemple personnalisé)
def detect_outliers_custom(valeurs_emg):
    """Exemple de méthode de détection d'outliers personnalisée."""
    # Appliquez une logique de détection personnalisée ici
    return []

# Isolation Forest
def detect_outliers_isolation_forest(valeurs_emg):
    """Détection des outliers à l'aide de Isolation Forest."""
    model = IsolationForest(contamination=0.1)  # Ajustez la contamination selon vos besoins
    valeurs_emg_array = np.array(valeurs_emg).reshape(-1, 1)
    predictions = model.fit_predict(valeurs_emg_array)
    outliers_if = np.where(predictions == -1)[0]  # Index des outliers
    return outliers_if

# Affichage du graphique avec les méthodes activées
def plot_emg_with_all_outliers(valeurs_emg, dead_points, outliers_ecart_type, outliers_iqr, outliers_custom, outliers_if, antoine_points):
    plt.figure(figsize=(10, 6))
    plt.plot(valeurs_emg, label="Valeurs EMG", color="b")
    
    if ACTIVER_DETECTION_POINTS_MORTS:
        plt.scatter(dead_points, [valeurs_emg[i] for i in dead_points], color="r", label="Points morts")
    
    if ACTIVER_DETECTION_OUTLIERS_ECART_TYPE:
        plt.scatter(outliers_ecart_type, [valeurs_emg[i] for i in outliers_ecart_type], color="g", label="Outliers (écart-type)")
    
    if ACTIVER_DETECTION_OUTLIERS_IQR:
        plt.scatter(outliers_iqr, [valeurs_emg[i] for i in outliers_iqr], color="orange", label="Outliers (IQR)")
    
    if ACTIVER_DETECTION_ANTOINE:
        plt.scatter(antoine_points, [valeurs_emg[i] for i in antoine_points], color="purple", label="Points Antoine")
    
    if ACTIVER_DETECTION_OUTLIERS_CUSTOM:
        plt.scatter(outliers_custom, [valeurs_emg[i] for i in outliers_custom], color="pink", label="Outliers (custom)")
    
    if ACTIVER_ISOLATION_FOREST:
        plt.scatter(outliers_if, [valeurs_emg[i] for i in outliers_if], color="yellow", label="Outliers (Isolation Forest)")
    
    plt.title("Graphique des valeurs EMG avec détection des anomalies")
    plt.xlabel("Index")
    plt.ylabel("Valeur EMG")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

# Exemple d'utilisation
ID_JOUEUR = 1  # Remplacez par l'ID du joueur que vous voulez analyser

# Récupérer les données EMG et les détecter
resultat = EMG_game_extraction(ID_JOUEUR)

# Si des données ont été récupérées, afficher le graphique
if resultat:
    dernier_session_id = list(resultat.keys())[0]
    valeurs_emg = resultat[dernier_session_id]["valeurs_emg"]
    dead_points = resultat[dernier_session_id]["dead_points"]
    outliers_ecart_type = resultat[dernier_session_id]["outliers_ecart_type"]
    outliers_iqr = resultat[dernier_session_id]["outliers_iqr"]
    outliers_custom = resultat[dernier_session_id]["outliers_custom"]
    outliers_if = resultat[dernier_session_id]["outliers_if"]
    antoine_points = resultat[dernier_session_id]["antoine_points"]
    
    # Afficher le graphique avec les points morts, outliers et points antoine
    plot_emg_with_all_outliers(valeurs_emg, dead_points, outliers_ecart_type, outliers_iqr, outliers_custom, outliers_if, antoine_points)
