import asyncio
from bleak import BleakScanner

async def scan_ble_devices():
    print("Recherche des périphériques Bluetooth Low Energy...")
    devices = await BleakScanner.discover()
    if devices:
        print("Périphériques détectés :")
        for device in devices:
            name = device.name if device.name else "Nom inconnu"
            print(f"Nom : {name}, Adresse : {device.address}")
    else:
        print("Aucun périphérique BLE détecté.")

# Exécuter l'analyse
asyncio.run(scan_ble_devices())