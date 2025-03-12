import sqlite3
import matplotlib.pyplot as plt
import numpy as np

ID_JOUEUR = 1   #Argument

# Fonction d'extraction des données depuis la base de données
def PPG_game_extraction():
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")  # Lien tablette Antoine
        #connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\Sleevy_App\instance\sleevy.db")
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Requête pour récupérer tous les session_id distincts associés à idjoueur = 1, triés par ordre croissant
        requete_session_ids = """
        SELECT DISTINCT session_id
        FROM sleevyppg
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
            # Récupération des valeurs PPG pour ce session_id
            requete_valeurs = """
            SELECT valeurppg
            FROM sleevyppg 
            WHERE idjoueur = ? AND session_id = ?;
            """
    
            curseur.execute(requete_valeurs, (ID_JOUEUR, session_id,))
            result = curseur.fetchall()  # Récupère toutes les valeurs sous forme de liste de tuples

            valeurs_ppg = [row[0] for row in result]  # Convertit en liste simple
            session_data[session_id] = valeurs_ppg  # Stocke dans le dictionnaire

            print(f"Session {session_id}: {', '.join(map(str, valeurs_ppg))}")
        
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

# Tracé des séries classées
def plot_ranked_series(datasets, reference_mean, ranked_labels):
    """Trace les séries classées (ranked) avec la variabilité par rapport à la référence."""
    fig, axs = plt.subplots(len(ranked_labels), 1, figsize=(12, len(ranked_labels) * 2), sharex=True)
    colors = plt.cm.tab10(np.linspace(0, 1, len(ranked_labels)))

    for i, label in enumerate(ranked_labels):
        data = datasets[label]
        valid_indices = [j for j, x in enumerate(data) if x is not None]
        valid_data = [data[j] for j in valid_indices]
        variability = sum(abs(x - reference_mean) for x in valid_data)

        axs[i].plot(valid_indices, valid_data, label=label, color=colors[i])
        axs[i].axhline(y=reference_mean, color='gray', linestyle='--', label=f'Ref. Mean: {reference_mean:.2f}')
        axs[i].fill_between(valid_indices, valid_data, reference_mean, color=colors[i], alpha=0.3)
        axs[i].set_title(f'{label} (Ref. Mean: {reference_mean:.2f}, Variability: {variability:.2f})')
        axs[i].legend()
        axs[i].grid(True)

    plt.tight_layout()
    plt.show()

# Tracé des variabilités cumulées pour chaque groupe
def plot_grouped_cumulative_variability(groups, cumulative_variabilities, variabilities):
    """Trace la variabilité cumulée pour chaque groupe."""
    fig, axs = plt.subplots(len(groups), 1, figsize=(12, len(groups) * 4), sharex=True)
    colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))

    for i, (group_variability, labels) in enumerate(groups.items()):
        ax = axs[i] if len(groups) > 1 else axs  # Gérer le cas d'un seul groupe
        for label in labels:
            group_cumulative_variability = cumulative_variabilities[label]
            ax.plot(
                range(len(group_cumulative_variability)),
                group_cumulative_variability,
                label=f"{label} (Var: {variabilities[label]:.2f})",
                color=colors[i],
            )

        ax.set_title(f"Groupe {i + 1} (Variabilité ~ {group_variability:.2f})")
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

    datasets = {f"Session_{session_id}": values for session_id, values in session_data.items()}

    reference_mean = 69.4  # Valeur de la référence moyenne
    cumulative_variabilities = {label: compute_cumulative_variability(data, reference_mean) for label, data in datasets.items()}
    variabilities = calculate_variabilities(datasets, reference_mean)
    tolerance = 0.2 * np.mean(list(variabilities.values()))
    groups = group_datasets_by_variability(variabilities, tolerance)

    ranked_labels = list(datasets.keys())

    plot_ranked_series(datasets, reference_mean, ranked_labels)
    plot_grouped_cumulative_variability(groups, cumulative_variabilities, variabilities)

    for i, (group_variability, labels) in enumerate(groups.items(), 1):
        print(f"Groupe {i} (Variabilité ~ {group_variability:.2f}): {', '.join(labels)}")

if __name__ == "__main__":
    main()
