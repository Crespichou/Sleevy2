import serial
import time

# Configurer la connexion série (ajustez le port COM si nécessaire)
ser = serial.Serial('COM3', 9600)  # Remplacez 'COM3' par le port correct pour votre Arduino

# Demander à l'utilisateur si il veut commencer la collecte
print("Collecte des données... Appuyez sur Ctrl+C pour arrêter.")
try:
    while True:
        # Lire les données envoyées par l'Arduino
        raw_data = ser.readline().strip()  # Lire la ligne et enlever les espaces
        if raw_data:  # Vérifier que la donnée n'est pas vide
            try:
                emg_value = int(raw_data)  # Convertir en entier
                print(f"Valeur EMG : {emg_value}")  # Afficher la valeur dans le terminal
            except ValueError:
                # Si la conversion échoue, ignorer la ligne
                continue
        time.sleep(0.1)  # Attendre 100 ms (comme dans le code Arduino)

except KeyboardInterrupt:
    # Arrêter proprement le programme avec Ctrl+C
    print("\nArrêt du programme.")

# Fermer la connexion série
ser.close()
