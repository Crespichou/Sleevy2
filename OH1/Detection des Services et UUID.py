import asyncio
from bleak import BleakClient

# Remplacez cette adresse par l'adresse de votre périphérique Polar
DEVICE_ADDRESS = "A0:9E:1A:E0:BC:4D"

async def read_polar_ppg():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connecté à {DEVICE_ADDRESS}")
        
        # Lister tous les services et caractéristiques
        services = await client.get_services()
        print("Services et caractéristiques disponibles :")
        for service in services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  - Caractéristique: {char.uuid}, propriétés: {char.properties}")

        # Identifier la caractéristique correspondant au PPG
        # (Remplacez par l'UUID de votre caractéristique PPG une fois connue)
        PPG_CHARACTERISTIC_UUID = "UUID_DE_LA_CARACTÉRISTIQUE_PPG"  
        
        if PPG_CHARACTERISTIC_UUID in [char.uuid for char in services.characteristics]:
            # Lire une valeur unique (si lecture directe)
            ppg_value = await client.read_gatt_char(PPG_CHARACTERISTIC_UUID)
            print(f"Valeur PPG : {ppg_value}")
        else:
            print("Caractéristique PPG non trouvée.")

# Exécution
asyncio.run(read_polar_ppg())
