"""
main.py — Primary application logic for the Speed Challenge race system.
"""

from datetime import datetime
import threading
import time
import sys

from src.core.networking.socket_io import SocketClient
from src.core.constants.pins import PIN_FINISH_BUTTON
from src.core.modules.button import Button

from src.functional.printer_manager import PrinterManager
from src.functional.high_score_lcd import HighScoreLCD
from src.functional.race_manager import RaceManager
from src.functional.race_sounds import RaceSounds
from src.functional.timer import RaceTimer
from src.core.system.storage import Storage

# Global instances for thread access
global_timer = None
current_race_id = None

client = SocketClient()
race_manager = RaceManager()

def refresh_loop(timer, stop_event):
    """Background thread to keep the 7-segment display multiplexing."""
    while not stop_event.is_set():
        timer.refresh()
        time.sleep(0.001)

def heartbeat_loop(client, timer, stop_event):
    """Sends a 'device-ready' signal every 5 seconds if a race is NOT running."""
    while not stop_event.is_set():
        if timer and not timer.running:
            client.sio.emit("send_message", "[end-pilar]-device-ready")
        
        for _ in range(50):
            if stop_event.is_set():
                break
            time.sleep(0.1)

def main():
    global global_timer, current_race_id
    
    # 1. Setup Socket Connection
    client.connect()

    # 2. Initialize Audio System
    race_sounds = RaceSounds()

    # 3. Clear high score
    storage = Storage()
    storage.save("races.json", [])

    # 4. Initialize Hardware via Context Managers
    # We voegen de LED op pin 17 toe aan de Button constructor
    with RaceTimer() as timer, \
         HighScoreLCD() as hs, \
         Button(btn_pin=PIN_FINISH_BUTTON, led_pin=17) as button, \
         PrinterManager() as printer:
        
        global_timer = timer
        hs.set(race_manager.get_high_score())
        
        # Start-status: LED is uit
        button.set_led_state(0)

        def on_finish_line_crossed():
            """Handles the logic when the physical finish button is pressed."""
            global current_race_id
            
            if timer.running and current_race_id is not None:
                # LED direct UIT bij finish
                button.set_led_state(0)
                
                race_to_stop = current_race_id
                current_race_id = None
                
                timer.stop()
                race_sounds.play_finish_bell()
                
                end_iso = datetime.now().isoformat() + "Z"
                elapsed_ms = timer.elapsed * 1000

                printer.print_speed_result(timer.elapsed)
                race_manager.stop_race(race_to_stop, end_iso, elapsed_ms)
                hs.set(race_manager.get_high_score())
                
                print(f"\n■ FINISH! Race #{race_to_stop} completed: {timer.elapsed:.2f}s")
                print("> ", end="", flush=True)

        def start_race_sequence():
            """Helper to unify start logic for both manual and ESP32 triggers."""
            global current_race_id
            if timer.start():
                # LED gaat PULSEREN bij start
                button.set_led_state(2)
                
                start_iso = datetime.now().isoformat() + "Z"
                current_race_id = race_manager.start_new_race(start_iso)
                return True
            return False

        # Assign hardware interrupt
        button.on_press(on_finish_line_crossed)
        
        # Setup threads
        stop_event = threading.Event()
        refresh_thread = threading.Thread(target=refresh_loop, args=(timer, stop_event), daemon=True)
        refresh_thread.start()

        heartbeat_thread = threading.Thread(target=heartbeat_loop, args=(client, timer, stop_event), daemon=True)
        heartbeat_thread.start()

        # Handle ESP32 (Start Pillar) events
        @client.sio.on("button_pressed")
        def handle_esp_event(data):
            if start_race_sequence():
                print(f"\n[SocketIO] ▶ Race #{current_race_id} started via ESP32!")
                print("> ", end="", flush=True)

        print("--- Speed Challenge System Ready ---")
        print("Commands: 's' (start), 't' (stop), 'r' (reset), 'q' (quit)")

        try:
            while True:
                command = None
                if sys.stdin and sys.stdin.isatty():
                    command = input("> ").strip().lower()
                else:
                    # Background mode
                    time.sleep(1)
                    continue

                if command == "s":
                    if start_race_sequence():
                        print(f"▶ Manual Start: Race #{current_race_id}")
                
                elif command == "t":
                    on_finish_line_crossed()

                elif command == "r":
                    timer.reset()
                    button.set_led_state(0) # Ook LED uit bij reset
                    current_race_id = None
                    print("↺ System Reset")
                
                elif command == "q":
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            stop_event.set()
            client.disconnect()
            race_sounds.cleanup()
            refresh_thread.join(timeout=1)
            heartbeat_thread.join(timeout=1)

if __name__ == "__main__":
    main()