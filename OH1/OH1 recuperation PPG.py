import asyncio
from bleak import BleakClient

# Remplacez par l'adresse de votre capteur et l'UUID de la caractéristique
DEVICE_ADDRESS = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Fonction pour traiter les notifications
def handle_notification(sender, data):
    # Convertir les données reçues (en bytes) en entier
    try:
        # Si les données sont en bytes, utilisez int.from_bytes pour les convertir
        ppg_value = int.from_bytes(data, byteorder="big")
#        ppg_value2 = ppg_value / 260
        
        print(f"Données PPG : {ppg_value}")
    except Exception as e:
        print(f"Erreur de décodage : {e}")

async def receive_ppg_notifications():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connecté à {DEVICE_ADDRESS}")

        # S'abonner aux notifications PPG
        try:
            await client.start_notify(PPG_CHARACTERISTIC_UUID, handle_notification)
            print("Abonnement aux notifications PPG...")

            # Reste connecté pendant 30 secondes
            await asyncio.sleep(120)

            await client.stop_notify(PPG_CHARACTERISTIC_UUID)
            print("Notifications arrêtées.")
        except Exception as e:
            print(f"Erreur lors de l'abonnement : {e}")

# Exécution de l'abonnement
asyncio.run(receive_ppg_notifications())