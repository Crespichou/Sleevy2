def monitor_stop_event(stop_event):
    while not stop_event.is_set():
        command = input("Type 'stop' to end the simulation: ").strip().lower()
        if command == "stop":
            stop_event.set()