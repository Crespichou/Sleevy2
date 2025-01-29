from multiprocessing import Event
import threading
from BPM import main as bpm_main
from Accel import simulate_accel
from Event import monitor_stop_event

# Listes pour stocker les valeurs BPM et Accélération
bpm_values = []
accel_values = []

# Fonction pour exécuter BPM.py
def run_bpm(stop_event):
    global bpm_values
    try:
        bpm_values = bpm_main(stop_event)
    except Exception as e:
        print(f"Erreur dans run_bpm : {e}")

# Fonction pour exécuter la simulation d'Accélération
def run_accel(stop_event):
    global accel_values
    try:
        # simulate_accel est un générateur qui retourne des valeurs d'accélération
        for accel in simulate_accel(stop_event):
            accel_values.append(accel)  # Ajoute chaque valeur d'accélération à la liste
    except Exception as e:
        print(f"Erreur dans run_accel : {e}")

# Fonction principale
def main():
    stop_event = Event()

    # Création des threads
    bpm_thread = threading.Thread(target=run_bpm, args=(stop_event,))
    accel_thread = threading.Thread(target=run_accel, args=(stop_event,))
    stop_thread = threading.Thread(target=monitor_stop_event, args=(stop_event,))

    # Démarrage des threads
    bpm_thread.start()
    accel_thread.start()
    stop_thread.start()

    # Attente de la fin des threads
    bpm_thread.join()
    accel_thread.join()
    stop_thread.join()

    # Affichage des résultats
    print("\n BPM mesurés :")
    print(bpm_values)

    print("\n Accéléromètres mesurés :")
    print(accel_values)

if __name__ == "__main__":
    main()
