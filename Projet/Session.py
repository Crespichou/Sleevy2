import asyncio
import time
import threading
import serial
from bleak import BleakClient
from threading import Event
from Event import monitor_stop_event

# Paramètres pour la collecte EMG
ser = serial.Serial('COM3', 9600) 
emg_values = []

# Paramètres pour la collecte PPG
DEVICE_ADDRESS = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
ppg_values = []

"""Fonction de récolte EMG"""
# Fonction pour gérer les notifications EMG
def emg(stop_event):
    try:
        while not stop_event.is_set():  
            raw_data = ser.readline().strip()  
            if raw_data:  
                try:
                    emg_value = int(raw_data)  
                    emg_values.append(emg_value) 
                except ValueError:
                    continue
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("\nArrêt du programme EMG.")
    ser.close()


"""Fonction de récolte PPG"""
def handle_notification(sender, data):
    try:
        ppg_value = int.from_bytes(data, byteorder="big")
        ppg_values.append(ppg_value)
    except Exception as e:
        print(f"Erreur de décodage PPG : {e}")

async def receive_ppg_notifications(stop_event):
    async with BleakClient(DEVICE_ADDRESS) as client:
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



"""Fonction de lancement simultané"""
def main():
    # Création d'un objet stop_event
    stop_event = Event()

    # Démarrage du thread EMG
    emg_thread = threading.Thread(target=emg, args=(stop_event,))
    emg_thread.start()

    # Démarrage du thread PPG
    ppg_thread = threading.Thread(target=main_ppg, args=(stop_event,))
    ppg_thread.start()

    # Surveillance de l'événement de stop dans le thread principal
    monitor_stop_event(stop_event)

    # Attendre que les threads EMG et PPG se terminent
    emg_thread.join()
    ppg_thread.join()

    # Affichage des résultats
    print("Simulation terminée.")
    print(f"Valeurs EMG collectées : {emg_values}")
    print(f"Valeurs PPG collectées : {ppg_values}")

if __name__ == "__main__":
    main()
