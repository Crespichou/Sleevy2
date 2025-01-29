# BPM.py
import asyncio
from bleak import BleakClient
from threading import Event, Thread

DEVICE_ADDRESS = "A0:9E:1A:E0:BC:4D"
PPG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
ppg_values = []

def handle_notification(sender, data):
    try:
        ppg_value = int.from_bytes(data, byteorder="big")
        ppg_values.append(ppg_value)
    except Exception as e:
        print(f"Erreur de décodage : {e}")

async def receive_ppg_notifications(stop_event):
    async with BleakClient(DEVICE_ADDRESS) as client:
        try:
            await client.start_notify(PPG_CHARACTERISTIC_UUID, handle_notification)
            while not stop_event.is_set():  
                await asyncio.sleep(1)
            await client.stop_notify(PPG_CHARACTERISTIC_UUID)
        except Exception as e:
            print(f"Erreur lors de l'abonnement : {e}")

def main(stop_event):
    try:
        asyncio.run(receive_ppg_notifications(stop_event))
    except Exception as e:
        print(f"Erreur dans la boucle asyncio : {e}")
    return ppg_values
