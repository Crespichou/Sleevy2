import sqlite3
import numpy as np
import matplotlib.pyplot as plt

def EMG_game_extraction(ID_JOUEUR):
    """
    Extrait les données EMG pour un joueur donné à partir de la base de données.
    Retourne les valeurs EMG et les points brutaux pour la dernière session.
    """
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")
        print("Connexion réussie.")

        curseur = connexion.cursor()

        curseur.execute("SELECT DISTINCT session_id FROM sleevyemg WHERE idjoueur = ? ORDER BY session_id ASC;", (ID_JOUEUR,))
        session_ids = [row[0] for row in curseur.fetchall()]
        if not session_ids:
            print("Aucune session trouvée.")
            connexion.close()
            return {}
        dernier_session_id = session_ids[-1]

        curseur.execute("SELECT valeuremg FROM sleevyemg WHERE idjoueur = ? AND session_id = ?;", (ID_JOUEUR, dernier_session_id))
        valeurs_emg = [row[0] for row in curseur.fetchall()]
        connexion.close()

        points_brutaux = detection_brutale(valeurs_emg, group_size=70, seuil_diff=0.6)

        return {
            dernier_session_id: {
                "valeurs_emg": valeurs_emg,
                "points_brutaux": points_brutaux
            }
        }
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)
        return None

def calculer_pente(valeurs):
    """
    Calcule la pente (coef directeur) d'une série de valeurs.
    """
    x = np.arange(len(valeurs))
    y = np.array(valeurs)
    if len(x) > 1:
        pente = (y[-1] - y[0]) / (x[-1] - x[0])
    else:
        pente = 0
    return pente

def detection_brutale(valeurs_emg, group_size=20, seuil_diff=5):
    """
    Détecte les points brutaux dans les données EMG en utilisant une moyenne mobile.
    """
    points = []
    moyenne_mobile = np.convolve(valeurs_emg, np.ones(group_size) / group_size, mode="valid")
    i = 0
    while i < len(moyenne_mobile) - 30:
        valeurs_premiere_periode = moyenne_mobile[i:i + 30]
        pente_premiere = calculer_pente(valeurs_premiere_periode)
        valeurs_seconde_periode = moyenne_mobile[i + 30:i + 60]
        pente_seconde = calculer_pente(valeurs_seconde_periode)

        if np.abs(pente_premiere - pente_seconde) < seuil_diff:
            i += 30
        else:
            points.append(i + 30)
            i += 30
    return points

def diviser_par_points(valeurs_emg, points_brutaux):
    """
    Divise les valeurs EMG en segments basés sur les points brutaux détectés.
    """
    segments = []
    start_idx = 0
    for point in points_brutaux:
        segments.append((start_idx, point, valeurs_emg[start_idx:point]))
        start_idx = point
    segments.append((start_idx, len(valeurs_emg), valeurs_emg[start_idx:]))
    return segments

def plot_emg_with_detections(valeurs_emg, points_brutaux, segments, group_size=20,
                             show_moyenne_mobile=True, show_points_brutaux=True,
                             show_negative_segments=True, fill_negative_segments=True):
    """
    Trace les valeurs EMG et met en évidence les segments avec une pente négative.
    """
    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.25)

    plt.plot(valeurs_emg, label="Valeurs EMG", color="b")

    moyenne_mobile = np.convolve(valeurs_emg, np.ones(group_size) / group_size, mode="valid")
    if show_moyenne_mobile:
        plt.plot(range(group_size - 1, len(valeurs_emg)), moyenne_mobile, label="Moyenne mobile", color="orange", linestyle='--')

    if show_points_brutaux:
        plt.scatter(points_brutaux, [moyenne_mobile[i] for i in points_brutaux], color="red", label="Points Brutaux", zorder=5)

    segments_sorted = sorted(segments, key=lambda s: len(s[2]), reverse=True)
    top_segments = segments_sorted[:6]

    negative_segments = [(start, end, calculer_pente(segment)) for start, end, segment in top_segments if calculer_pente(segment) < 0]

    legend_text = [f"Nombre de diminutions d'intensité : {len(negative_segments)}"]
    for start, end, pente in negative_segments:
        if -0.03 <= pente < 0:
            legend_text.append(f"{start} à {end}, Pente: {pente:.2f} ▼ Diminution faible")
        elif -0.06 <= pente < -0.03:
            legend_text.append(f"{start} à {end}, Pente: {pente:.2f} ▼ Diminution forte")
        else:
            legend_text.append(f"{start} à {end}, Pente: {pente:.2f} ▼ Où sont tes muscles ?")

    legend_text = "\n".join(legend_text)

    for start, end, segment in top_segments:
        pente = calculer_pente(segment)
        x_vals = np.arange(start, end)
        y_vals = np.array(segment) + pente * (x_vals - start)

        if show_negative_segments and pente < 0:
            color = "red"
            plt.plot(x_vals, y_vals, color=color, linestyle='--', alpha=0.3)

            if fill_negative_segments:
                plt.fill_between(x_vals, y_vals, color=color, alpha=0.05)

    plt.title("Activité musculaire de votre game")
    plt.xlabel("Temps")
    plt.ylabel("Valeur EMG")
    plt.grid(True)

    plt.figtext(0.5, 0.1, legend_text, ha="center", fontsize=10, fontweight="bold", color="black",
                bbox={"facecolor": "white", "alpha": 0.6, "pad": 8}, fontfamily="monospace")

    plt.show()

def main():
    """
    Fonction principale pour exécuter l'extraction des données et le traçage du graphique.
    """
    ID_JOUEUR = 1
    resultat = EMG_game_extraction(ID_JOUEUR)

    if resultat:
        session_id = list(resultat.keys())[0]
        valeurs_emg = resultat[session_id]["valeurs_emg"]
        points_brutaux = resultat[session_id]["points_brutaux"]

        segments = diviser_par_points(valeurs_emg, points_brutaux)

        plot_emg_with_detections(valeurs_emg, points_brutaux, segments,
                                 show_moyenne_mobile=True,
                                 show_points_brutaux=True,
                                 show_negative_segments=False,
                                 fill_negative_segments=False)

if __name__ == "__main__":
    main()
