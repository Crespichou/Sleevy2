import asyncio
import signal
from bleak import BleakClient
import pandas as pd  # Pour manipuler et enregistrer des fichiers Excel
import os  # Pour vérifier si le fichier Excel existe

# Adresse du périphérique et UUID de la caractéristique
DEVICE_ADDRESS = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Liste pour stocker les données PPG
ppg_data_list = []

# Variable pour contrôler l'exécution
running = True

# Nom du fichier Excel
excel_filename = "PPG_data.xlsx"

# Charger les données existantes si le fichier existe
if os.path.exists(excel_filename):
    df = pd.read_excel(excel_filename, engine='openpyxl')
else:
    df = pd.DataFrame()

# Demander le numéro de série à l'utilisateur
serie_number = input("Veuillez entrer le numéro de la série de mesure : ")

# Vérifier si le numéro de série existe déjà dans le fichier
if f"Série {serie_number}" in df.columns:
    print(f"Erreur : Une série avec le numéro {serie_number} existe déjà dans le fichier '{excel_filename}'.")
    exit()  # Quitter le programme si le numéro de série existe déjà

# Fonction pour traiter les notifications
def handle_notification(sender, data):
    try:
        # Convertir les données reçues (en bytes) en entier
        ppg_value = int.from_bytes(data, byteorder="big")
        ppg_data_list.append(ppg_value)
        print(f"Données PPG : {ppg_value}")
    except Exception as e:
        print(f"Erreur de décodage : {e}")

# Fonction pour capturer l'arrêt manuel
def stop_program(signal_received, frame):
    global running
    print("\nSignal reçu. Arrêt du programme en cours...")
    running = False

async def receive_ppg_notifications():
    global running
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connecté à {DEVICE_ADDRESS}")

        # S'abonner aux notifications PPG
        try:
            await client.start_notify(PPG_CHARACTERISTIC_UUID, handle_notification)
            print("Abonnement aux notifications PPG...")

            while running:
                # Attendre 1 seconde avant de vérifier si le programme doit s'arrêter
                await asyncio.sleep(1)

            await client.stop_notify(PPG_CHARACTERISTIC_UUID)
            print("Notifications arrêtées.")
        except Exception as e:
            print(f"Erreur lors de l'abonnement : {e}")

# Configurer le gestionnaire de signal pour arrêter le programme proprement
signal.signal(signal.SIGINT, stop_program)

# Exécution de l'abonnement
try:
    asyncio.run(receive_ppg_notifications())
finally:
    # Enregistrer les données collectées dans un fichier Excel
    print("\nProgramme terminé. Données collectées :")
    print(ppg_data_list)

    # Ajouter les nouvelles données dans une colonne avec le numéro de série
    df[f"Série {serie_number}"] = pd.Series(ppg_data_list)

    # Sauvegarder les données mises à jour dans le fichier Excel
    df.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"Les données ont été ajoutées dans le fichier '{excel_filename}'.")
