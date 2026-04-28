"""
src/core/sound.py — Generic hardware driver for a passive piezo buzzer via PWM.

This module provides high-level control over a buzzer, allowing for custom 
melodies and rhythmic sequences by bypassing standard tonal safety limits.

Requires:
    pip install gpiozero lgpio

Usage:
    from src.core.modules.sound import SoundController

    sc = SoundController()
    sequence = [{'pitch': 2700, 'ms': 100, 'pause': 50}, ...]
    sc.play_sequence(sequence)
    sc.cleanup()

Technical Info:
    - Resonance Zone: 1000Hz - 2700Hz (Maximum Volume).
    - Duty Cycle: Fixed at 50% (value=0.5) for max physical displacement.
    - Pitch 0: Functions as a silent rest.
"""

from gpiozero import PWMOutputDevice
import time

from src.core.constants.pins import PIN_BUZZER

class SoundController:
    def __init__(self, pin=PIN_BUZZER):
        """Initializes the hardware PWM device on the specified GPIO pin."""
        self.buzzer = PWMOutputDevice(pin)

    def play_sequence(self, sequence):
        """
        Plays an array of sound dictionaries.
        Format: [{'pitch': 2700, 'ms': 100, 'pause': 50}, ...]
        """
        try:
            for note in sequence:
                pitch = note.get('pitch', 1000)
                duration_sec = note.get('ms', 100) / 1000.0
                pause_sec = note.get('pause', 0) / 1000.0

                if pitch > 0:
                    self.buzzer.frequency = pitch
                    self.buzzer.value = 0.5  # Max volume for square wave
                    time.sleep(duration_sec)
                    self.buzzer.value = 0
                else:
                    # Treat pitch 0 as a rest/silence
                    time.sleep(duration_sec)
                
                if pause_sec > 0:
                    time.sleep(pause_sec)
        except Exception as e:
            print(f"[Sound Core Error] {e}")
            self.buzzer.value = 0

    def cleanup(self):
        """Ensures the GPIO pin is released properly."""
        self.buzzer.close()