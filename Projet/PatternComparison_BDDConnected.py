import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Fonction d'extraction des données depuis la base de données
def PPG_game_extraction():
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db")  # Lien tablette Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Requête pour récupérer tous les session_id distincts associés à idjoueur = 1, triés par ordre croissant
        requete_session_ids = """
        SELECT DISTINCT session_id
        FROM sleevyppg
        WHERE idjoueur = 1
        ORDER BY session_id ASC;
        """

        curseur.execute(requete_session_ids)
        session_ids = [row[0] for row in curseur.fetchall()]
        
        if not session_ids:
            print("Aucune session trouvée.")
            connexion.close()
            return {}

        last_session_id = session_ids[-1]  # Récupération du dernier session_id
        session_ids.pop()  # Suppression du dernier session_id de la liste

        session_data = {}  # Dictionnaire pour stocker les données

        for session_id in session_ids:
            # Récupération des valeurs PPG pour ce session_id
            requete_valeurs = """
            SELECT valeurppg
            FROM sleevyppg 
            WHERE idjoueur = 1 AND session_id = ?;
            """
    
            curseur.execute(requete_valeurs, (session_id,))
            result = curseur.fetchall()  # Récupère toutes les valeurs sous forme de liste de tuples

            valeurs_ppg = [row[0] for row in result]  # Convertit en liste simple
            session_data[session_id] = valeurs_ppg  # Stocke dans le dictionnaire

            print(f"Session {session_id}: {', '.join(map(str, valeurs_ppg))}")
        
        # Ajout du dernier session_id
        requete_valeurs = """
        SELECT valeurppg
        FROM sleevyppg 
        WHERE idjoueur = 1 AND session_id = ?;
        """
        curseur.execute(requete_valeurs, (last_session_id,))
        result = curseur.fetchall()  # Récupère toutes les valeurs sous forme de liste de tuples

        valeurs_ppg = [row[0] for row in result]  # Convertit en liste simple
        session_data[last_session_id] = valeurs_ppg  # Stocke dans le dictionnaire

        print(f"Session {last_session_id}: {', '.join(map(str, valeurs_ppg))}")
        
        connexion.close()
        return session_data  # Retourne le dictionnaire contenant les données
    
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)
        return None

# Calcul de la variabilité cumulée
def compute_cumulative_variability(data, fixed_mean):
    """Calcule la variabilité cumulée par rapport à une moyenne fixe."""
    cumulative_variability = []
    current_variability = 0
    for value in data:
        if value is not None:
            current_variability += abs(value - fixed_mean)
            cumulative_variability.append(current_variability)
    return cumulative_variability

# Calcul des variabilités
def calculate_variabilities(datasets, reference_mean):
    """Calcule la variabilité totale pour chaque série de données."""
    return {
        label: sum(abs(x - reference_mean) for x in data if x is not None)
        for label, data in datasets.items()
    }

# Regroupement des données par variabilité
def group_datasets_by_variability(variabilities, tolerance):
    """Regroupe les séries en fonction de leur variabilité avec une tolérance donnée."""
    groups = {}
    for label, variability in variabilities.items():
        added_to_group = False
        for group_variability in groups:
            if abs(variability - group_variability) <= tolerance:
                groups[group_variability].append(label)
                added_to_group = True
                break
        if not added_to_group:
            groups[variability] = [label]
    return groups

# Tracé des séries chronologiques (avec la dernière session en couleur et les autres en noir et blanc)
def plot_grouped_ranked_series(datasets, reference_mean, last_session_id, last_session_group):
    """Trace les séries classées avec la dernière session en couleur et les autres en noir et blanc."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for label in last_session_group:
        data = datasets[label]
        valid_indices = [j for j, x in enumerate(data) if x is not None]
        valid_data = [data[j] for j in valid_indices]

        if label == last_session_id:  # Dernière session en couleur
            ax.plot(valid_indices, valid_data, label=f'{label}', color='red')
        else:  # Autres sessions en noir et blanc
            ax.plot(valid_indices, valid_data, label=f'{label}', color='black')

    ax.set_title("Séries Chronologiques pour les Sessions du Même Groupe")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Valeurs PPG")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

# Tracé des variabilités cumulées pour le groupe de la dernière session
def plot_grouped_cumulative_variability(groups, cumulative_variabilities, variabilities, last_session_group):
    """Trace la variabilité cumulée pour les sessions dans le même groupe que la dernière."""
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, len(last_session_group)))

    for i, label in enumerate(last_session_group):
        group_cumulative_variability = cumulative_variabilities[label]
        
        if label == last_session_group[0]:  # Dernière session en couleur
            ax.plot(
                range(len(group_cumulative_variability)),
                group_cumulative_variability,
                label=f"{label} (Var: {variabilities[label]:.2f})",
                color='red'
            )
        else:
            ax.plot(
                range(len(group_cumulative_variability)),
                group_cumulative_variability,
                label=f"{label} (Var: {variabilities[label]:.2f})",
                color='black'
            )

    ax.set_title("Variabilité Cumulée pour les Sessions du Même Groupe")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Variabilité cumulée")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

# Fonction principale
def main():
    session_data = PPG_game_extraction()  # Extraire les données de la base de données

    if not session_data:
        print("Aucune donnée à traiter.")
        return

    # Utilisation des données de la base pour l'analyse
    datasets = {}
    for session_id, values in session_data.items():
        datasets[f"Session_{session_id}"] = values

    reference_mean = 69.4  # Utilisation directe de la valeur de la référence moyenne
    cumulative_variabilities = {
        label: compute_cumulative_variability(data, reference_mean) for label, data in datasets.items()
    }
    variabilities = calculate_variabilities(datasets, reference_mean)
    tolerance = 0.1 * np.mean(list(variabilities.values()))
    groups = group_datasets_by_variability(variabilities, tolerance)

    ranked_labels = list(datasets.keys())  # Utiliser les labels des sessions comme labels rangés
    last_session_id = f"Session_{list(session_data.keys())[-1]}"  # Dernière session

    # Identifier le groupe contenant la dernière session
    last_session_group = None
    for group_variability, labels in groups.items():
        if last_session_id in labels:
            last_session_group = labels
            break

    if last_session_group:
        # Appels de fonctions pour générer les graphiques du groupe de la dernière session
        plot_grouped_ranked_series(datasets, reference_mean, last_session_id, last_session_group)
        plot_grouped_cumulative_variability(groups, cumulative_variabilities, variabilities, last_session_group)

# Vérifier si le script est exécuté directement (pas importé)
if __name__ == "__main__":
    main()
