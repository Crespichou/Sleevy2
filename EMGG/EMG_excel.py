import serial
import time
import pandas as pd
import os
import matplotlib.pyplot as plt

# Configurer la connexion série (ajustez le port COM si nécessaire)
ser = serial.Serial('COM3', 9600)  # Remplacez 'COM3' par le port correct pour votre Arduino

# Demander à l'utilisateur le nom de la série
series_name = input("Entrez le nom de la série pour cette session de mesures : ")

# Vérifier si le fichier Excel existe déjà
file_name = "EMG_data.xlsx"

# Si le fichier existe, vérifier les noms des onglets
if os.path.exists(file_name):
    try:
        # Lire les données existantes dans le fichier Excel
        df_existing = pd.read_excel(file_name, sheet_name=None)  # Lire tout le fichier (tous les onglets)
        sheet_names = df_existing.keys()  # Obtenir les noms des onglets (séries existantes)
        # Vérifier si la série existe déjà
        if series_name in sheet_names:
            print(f"Erreur : La série '{series_name}' existe déjà dans le fichier Excel.")
            exit()  # Arrêter le programme si la série existe déjà
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel : {e}")
        exit()
else:
    df_existing = None  # Si le fichier n'existe pas, pas de données existantes

# Liste pour stocker les valeurs EMG
emg_values = []

# Demander à l'utilisateur s'il souhaite commencer la collecte de données
print(f"Collecte des données pour la série : {series_name}")
try:
    while True:
        # Lire les données envoyées par l'Arduino
        raw_data = ser.readline().strip()  # Lire la ligne et enlever les espaces
        if raw_data:  # Vérifier que la donnée n'est pas vide
            try:
                emg_value = int(raw_data)  # Convertir en entier
                emg_values.append(emg_value)  # Ajouter la valeur à la liste
                print(emg_value)  # Afficher la valeur dans le terminal
            except ValueError:
                # Si la conversion échoue, ignorer la ligne
                continue
        time.sleep(0.05)  # Attendre 100 ms (comme dans le code Arduino)
except KeyboardInterrupt:
    # Arrêter proprement le programme avec Ctrl+C
    print("Arrêt du programme.")

# Fermer la connexion série
ser.close()

# Convertir les données EMG en DataFrame pandas pour l'enregistrement dans un fichier Excel
df_new_series = pd.DataFrame(emg_values, columns=[series_name])

# Si le fichier existe déjà, ajouter la nouvelle série sous forme de colonne
if df_existing is not None:
    try:
        # Ajouter la nouvelle colonne au DataFrame existant
        df_existing = df_existing[list(df_existing.keys())[0]]  # Accéder à la première feuille
        df_existing[series_name] = df_new_series[series_name]  # Ajouter la nouvelle série en colonne
        # Enregistrer les modifications dans le même fichier Excel
        with pd.ExcelWriter(file_name, mode='w', engine='openpyxl') as writer:
            df_existing.to_excel(writer, index=False)
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier Excel : {e}")
else:
    # Si le fichier n'existe pas, créer un nouveau fichier Excel
    df_new_series.to_excel(file_name, index=False)

print(f"Les données ont été enregistrées dans le fichier {file_name} sous la colonne '{series_name}'.")

# Affichage du graphique des mesures
plt.plot(emg_values)
plt.title(f"Graphique des valeurs EMG pour la série '{series_name}'")
plt.xlabel("Index de mesure")
plt.ylabel("Valeur EMG")
plt.grid(True)
plt.show()
