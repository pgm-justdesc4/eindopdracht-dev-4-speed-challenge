"""
main.py — Primary application logic for the Speed Challenge race system.
"""

from datetime import datetime
import threading
import time

from src.core.networking.socket_io import SocketClient
from src.core.constants.pins import PIN_FINISH_BUTTON
from src.core.modules.button import Button

from src.functional.high_score_lcd import HighScoreLCD
from src.functional.race_manager import RaceManager
from src.functional.race_sounds import RaceSounds
from src.functional.timer import RaceTimer

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

def main():
    global global_timer, current_race_id
    
    # 1. Setup Socket Connection
    client.connect()

    # 2. Initialize Audio System
    # SoundController and Pin 4 are now handled internally within RaceSounds
    race_sounds = RaceSounds()

    # 3. Initialize Hardware via Context Managers
    with RaceTimer() as timer, HighScoreLCD() as hs, Button(PIN_FINISH_BUTTON) as button:
        
        global_timer = timer
        hs.set(race_manager.get_high_score())

        def on_finish_line_crossed():
            """Handles the logic when the physical finish button is pressed."""
            global current_race_id
            
            # Use current_race_id as a gatekeeper to prevent double-triggers
            if timer.running and current_race_id is not None:
                # Capture the current race ID and immediately reset it to prevent re-entry
                race_to_stop = current_race_id
                current_race_id = None
                
                # Stop hardware timer
                timer.stop()
                
                # Play the 'Ding-Ding-Dinggg' pattern
                race_sounds.play_finish_bell()
                
                # Process race data
                end_iso = datetime.now().isoformat() + "Z"
                elapsed_ms = timer.elapsed * 1000
                
                # Update records and display
                race_manager.stop_race(race_to_stop, end_iso, elapsed_ms)
                hs.set(race_manager.get_high_score())
                
                print(f"\n■ FINISH! Race #{race_to_stop} completed: {timer.elapsed:.2f}s")
                print("> ", end="", flush=True)

        # Assign hardware interrupt for finish line
        button.on_press(on_finish_line_crossed)
        
        # Start background refresh thread for 7-segment display
        stop_event = threading.Event()
        thread = threading.Thread(target=refresh_loop, args=(timer, stop_event), daemon=True)
        thread.start()

        # Handle ESP32 (Start Pillar) events via Socket.IO
        @client.sio.on("button_pressed")
        def handle_esp_event(data):
            global current_race_id
            if timer.start():
                start_iso = datetime.now().isoformat() + "Z"
                current_race_id = race_manager.start_new_race(start_iso)
                print(f"\n[SocketIO] ▶ Race #{current_race_id} started via ESP32!")
                print("> ", end="", flush=True)

        print("--- Speed Challenge System Ready ---")
        print("Commands: 's' (start), 't' (stop), 'r' (reset), 'q' (quit)")

        try:
            while True:
                command = input("> ").strip().lower()
                
                if command == "s":
                    if timer.start():
                        start_iso = datetime.now().isoformat() + "Z"
                        current_race_id = race_manager.start_new_race(start_iso)
                        print(f"▶ Manual Start: Race #{current_race_id}")
                
                elif command == "t":
                    print("■ Manual Stop: Time {:.2f}s".format(timer.elapsed))
                    on_finish_line_crossed()

                elif command == "r":
                    timer.reset()
                    current_race_id = None
                    print("↺ System Reset")
                
                elif command == "q":
                    break
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            pass
        finally:
            # Shutdown and Cleanup
            stop_event.set()
            client.disconnect()
            race_sounds.cleanup()
            thread.join(timeout=1)

if __name__ == "__main__":
    main()