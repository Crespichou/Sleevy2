#import asynciopip
import asyncio
import time
import threading
import serial
from bleak import BleakClient
from threading import Event
from Projet.Event import stop_event
import sqlite3
from datetime import datetime


def create_session(ID_JOUEUR):
    """Crée une nouvelle session dans la base de données pour acceuillir les données."""
    try:
        # Connexion à la base de données
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\Sleevy_App\instance\sleevy.db) #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")  # Lien PC Antoine
        curseur = connexion.cursor()
        
        # Recherche du dernier gamenumber du joueur
        requete_last_gamenumber = """
        SELECT gamenumber FROM sleevy_session WHERE idjoueur = ? ORDER BY session_id DESC LIMIT 1
        """
        curseur.execute(requete_last_gamenumber, (ID_JOUEUR,))
        dernier_gamenumber = curseur.fetchone()
        
        # Incrémentation du gamenumber
        gamenumber = (dernier_gamenumber[0] + 1) if dernier_gamenumber else 1
        
        # Définition des valeurs de la session
        starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        endtime = None  # La fin de session sera mise à jour plus tard
        
        # Requête d'insertion et création d'une session
        requete = """
        INSERT INTO sleevy_session (idjoueur, starttime, endtime, gamenumber)
        VALUES (?, ?, ?, ?)
        """
        
        curseur.execute(requete, (ID_JOUEUR, starttime, None, gamenumber))
        session_id = curseur.lastrowid  # Récupération de l'ID de la session créée
        
        connexion.commit()
        connexion.close()
        return session_id
        
    except sqlite3.Error as e:
        print("Erreur lors de la création de la session :", e)
        return None


def save_ppg_data(session_id, ppg_values,ID_JOUEUR):
    """Fonction d'ennregistrement des valeurs PPG dans la base de données."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")
        curseur = connexion.cursor()
        
        date_actuelle = datetime.now().strftime("%Y-%m-%d")
        #heure_actuelle = datetime.now().strftime("%H:%M:%S")
        
        requete = """
        INSERT INTO sleevyppg (idjoueur, session_id, valeurppg, dateppg, heureppg)
        VALUES (?, ?, ?, ?, ?)
        """
        
        curseur.executemany(requete, [(ID_JOUEUR, session_id, valeur, date_actuelle, timestamp) for valeur, timestamp in ppg_values])
        
        connexion.commit()
        connexion.close()
    except sqlite3.Error as e:
        print("Erreur lors de l'insertion des données PPG :", e)

def save_accel_data(session_id, accel_values, ID_JOUEUR) :
    """Fonction d'ennregistrement des valeurs PPG dans la base de données."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")
        curseur = connexion.cursor()
        
        date_actuelle = datetime.now().strftime("%Y-%m-%d")
        #heure_actuelle = datetime.now().strftime("%H:%M:%S")
        
        requete = """
        INSERT INTO sleevyaccelerometre (idjoueur, session_id, valeuraccel, dateaccel, heureaccel)
        VALUES (?, ?, ?, ?, ?)
        """
        
        curseur.executemany(requete, [(ID_JOUEUR, session_id, valeur, date_actuelle, timestamp) for valeur, timestamp in accel_values])
        
        connexion.commit()
        connexion.close()
    except sqlite3.Error as e:
        print("Erreur lors de l'insertion des données Accel :", e)

def save_emg_data(session_id, emg_values, ID_JOUEUR):
    """Fonction d'enregistrement des valeurs EMG dans la base de données."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")
        curseur = connexion.cursor()
        
        date_actuelle = datetime.now().strftime("%Y-%m-%d")
        #heure_actuelle = datetime.now().strftime("%H:%M:%S")
        
        requete = """
        INSERT INTO sleevyemg (idjoueur, session_id, valeuremg, dateemg, heureemg)
        VALUES (?, ?, ?, ?, ?)
        """
        
        curseur.executemany(requete, [(ID_JOUEUR, session_id, valeur, date_actuelle, timestamp) for valeur, timestamp in emg_values])
        
        connexion.commit()
        connexion.close()
    except sqlite3.Error as e:
        print("Erreur lors de l'insertion des données PPG :", e)


def update_endtime(session_id):
    """Met à jour l'heure de fin de la session."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\instance\sleevy.db")
        curseur = connexion.cursor()
        
        endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        requete = """
        UPDATE sleevy_session SET endtime = ? WHERE session_id = ?
        """
        
        curseur.execute(requete, (endtime, session_id))
        
        connexion.commit()
        connexion.close()
    except sqlite3.Error as e:
        print("Erreur lors de la mise à jour de endtime :", e)


# Paramètres pour la collecte EMG
ser = serial.Serial('COM3', 9600) 
emg_values = []

# Paramètres pour la collecte PPG
DEVICE_ADDRESS_PPG = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
ppg_values = []

# paramètre pour la collecte Accel
DEVICE_ADDRESS_ACCEL = "00:0C:BF:18:7C:2D"
ACCELEROMETER_CHARACTERISTIC_UUID = "49535343-1e4d-4bd9-ba61-23c647249616"
accel_values = []

"""Fonction de récolte EMG"""
def emg(stop_event):
    try:
        if not ser.is_open:
            ser.open()

        while not stop_event.is_set():
            if ser.is_open:
                raw_data = ser.readline().strip()
                if raw_data:
                    try:
                        emg_value = int(raw_data)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        emg_values.append((emg_value, timestamp))
                    except ValueError:
                        continue
            else:
                print("Le port série n'est pas ouvert.")
            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"Erreur de port série : {e}")
    except KeyboardInterrupt:
        print("\nArrêt du programme EMG.")
    finally:
        if ser.is_open:
            ser.close()



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

    
"""Fonction de récolte Accel"""
def handle_notification_accel(sender, data) :
    try :
        if len(data) >= 8 and data[0] == 0x55 and data[1] == 0x51:
            ax = int.from_bytes(data[2:4], byteorder='little', signed=True) / 32768.0 * 16.0
            ay = int.from_bytes(data[4:6], byteorder='little', signed=True) / 32768.0 * 16.0
            az = int.from_bytes(data[6:8], byteorder='little', signed=True) / 32768.0 * 16.0 -1
            max_accel = abs(az)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            accel_values.append((max_accel, timestamp))   
    except Exception as e:
        print(f"Erreur de décodage : {e}")

async def receive_accel_notifications(stop_event) :
    async with BleakClient(DEVICE_ADDRESS_ACCEL) as client:
        try : 
            await client.start_notify(ACCELEROMETER_CHARACTERISTIC_UUID, handle_notification_accel)
            while not stop_event.is_set():
                await asyncio.sleep(1)
            await client.stop_notify(ACCELEROMETER_CHARACTERISTIC_UUID)
        except Exception as e:
            print(f"Erreur lors de l'abonnement : {e}")
            
def main_accel(stop_event):
    try:
        asyncio.run(receive_accel_notifications(stop_event))
    except Exception as e:
        print(f"Erreur dans la boucle asyncio Accel : {e}")


def main(ID_JOUEUR):
    session_id = create_session(ID_JOUEUR)
    if session_id is None:
        print("Erreur lors de la création de la session. Arrêt du programme.")
        return


    emg_thread = threading.Thread(target=emg, args=(stop_event,))
    emg_thread.start()

    ppg_thread = threading.Thread(target=main_ppg, args=(stop_event,))
    ppg_thread.start()

    accel_thread = threading.Thread(target=main_accel, args=(stop_event,))
    accel_thread.start()

    
    stop_event.wait()
    update_endtime(session_id)
    
    emg_thread.join()
    ppg_thread.join()
    accel_thread.join()
    
    update_endtime(session_id)
    
    save_ppg_data(session_id, ppg_values, ID_JOUEUR)
    save_emg_data(session_id, emg_values, ID_JOUEUR)
    save_accel_data(session_id, accel_values, ID_JOUEUR)
    
    

    print(f"Simulation terminée. Session ID : {session_id}")
    #print(f"Valeurs EMG collectées : {emg_values}")
    #print(f"Valeurs PPG collectées : {ppg_values}")
    #print(f"Valeurs Accel collectées : {accel_values}")

if __name__ == "__main__":
    ID_JOUEUR = 3
    main(ID_JOUEUR)
