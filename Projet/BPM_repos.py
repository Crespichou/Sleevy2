import asyncio
import threading
from bleak import BleakClient
from threading import Event
from Projet.Event import monitor_stop_event
import sqlite3
from datetime import datetime


def save_ppg_data(ppg_values, ID_JOUEUR):
    """Fonction d'ennregistrement des valeurs PPG dans la base de données."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\Sleevy_App\instance\sleevy.db") #Tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")  # Lien PC Antoine
        curseur = connexion.cursor()
        
        requete = """
        INSERT INTO ppgreference (valeurppgrepos, heureppgrepos, idjoueur)
        VALUES (?, ?, ?)
        """
        
        curseur.executemany(requete, [(valeur, timestamp, ID_JOUEUR) for valeur, timestamp in ppg_values])
        
        connexion.commit()
        connexion.close()
    except sqlite3.Error as e:
        print("Erreur lors de l'insertion des données PPG :", e)

# Paramètres pour la collecte PPG
DEVICE_ADDRESS_PPG = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
ppg_values = []

"""Fonction de récolte PPG"""
def handle_notification(sender, data):
    try:
        ppg_value = int.from_bytes(data, byteorder="big")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ppg_values.append((ppg_value, timestamp))
    except Exception as e:
        print(f"Erreur de décodage PPG : {e}")

async def receive_ppg_notifications(stop_event):
    async with BleakClient(DEVICE_ADDRESS_PPG) as client:
        try:
            await client.start_notify(PPG_CHARACTERISTIC_UUID, handle_notification)
            while not stop_event.is_set():  
                await asyncio.sleep(1)
            await client.stop_notify(PPG_CHARACTERISTIC_UUID)
        except Exception as e:
            print(f"Erreur lors de l'abonnement PPG : {e}")

"""Fonction main de lancement"""
def main_ppg(stop_event):
    try:
        asyncio.run(receive_ppg_notifications(stop_event))
    except Exception as e:
        print(f"Erreur dans la boucle asyncio PPG : {e}")

def main(ID_JOUEUR) :
    stop_event = Event()

    ppg_thread = threading.Thread(target=main_ppg, args=(stop_event,))
    ppg_thread.start()

    monitor_stop_event(stop_event)

    ppg_thread.join()

    save_ppg_data(ppg_values, ID_JOUEUR)

    print(f"Valeurs PPG collectées : {ppg_values}")

if __name__ == "__main__":
    ID_JOUEUR = 4
    main(ID_JOUEUR) 