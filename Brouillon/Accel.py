def simulate_accel(stop_event):
    # Simulation d'une source de données Accélération
    import time
    import random
    while not stop_event.is_set():
        accel = random.choice([0, 1])
        yield accel  # Retourne la valeur via un générateur
        time.sleep(1)  # Simule un délai entre deux mesures
#YEAH KC>VIT
#KC>FNC