import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt


DEVICE_ADDRESS = "00:0C:BF:18:7C:2D"
ACCELEROMETER_CHARACTERISTIC_UUID = "49535343-1e4d-4bd9-ba61-23c647249616"

state = 0
max_accel_values = []

# 📡 Fonction pour traiter les données reçues
def handle_notification(sender, data):
    global state
    try:
        # Vérifier l'en-tête d'une trame d'accélération (ex: 0x55 0x51)
        if len(data) >= 8 and data[0] == 0x55 and data[1] == 0x51:
            ax = int.from_bytes(data[2:4], byteorder='little', signed=True) / 32768.0 * 16.0
            ay = int.from_bytes(data[4:6], byteorder='little', signed=True) / 32768.0 * 16.0
            az = int.from_bytes(data[6:8], byteorder='little', signed=True) / 32768.0 * 16.0 -1

            #print(f" Accélération - X: {ax:.2f}g, Y: {ay:.2f}g, Z: {az:.2f}g")

            
            max_accel = abs(az)
            max_accel_values.append(max_accel)

            # Vérification du dépassement de seuil
            if max_accel > 2:
                state = 1
            else:
                state = 0


    except Exception as e:
        print(f"Erreur de décodage : {e}")

async def receive_accel_notifications():
    try:
        async with BleakClient(DEVICE_ADDRESS) as client:
            print(f"✅ Connecté à {DEVICE_ADDRESS}")

            await client.start_notify(ACCELEROMETER_CHARACTERISTIC_UUID, handle_notification)
            #print("Abonnement aux notifications d'accélération...")

            # Reste connecté et écoute pendant 120 secondes
            await asyncio.sleep(120)

            await client.stop_notify(ACCELEROMETER_CHARACTERISTIC_UUID)
            print(" Notifications arrêtées.")

    except Exception as e:
        print(f"Erreur lors de l'abonnement : {e}")

# Lancement du programme
try:
    asyncio.run(receive_accel_notifications())
except KeyboardInterrupt:
    print("Interruption manuelle détectée.")
except Exception as e:
    print(f"Erreur inattendue : {e}")

# Tracer la courbe des valeurs maximales
plt.figure(figsize=(10, 6))
plt.plot(max_accel_values, label='Max Accélération (g)')
plt.xlabel('Itération')
plt.ylabel('Accélération maximale (g)')
plt.title('Valeurs maximales des accélérations absolues')
plt.legend()
plt.grid(True)
plt.show()
