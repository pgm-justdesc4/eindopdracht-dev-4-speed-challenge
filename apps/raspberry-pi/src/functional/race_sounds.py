"""
src/functional/race_sounds.py — High-level race sound patterns and feedback.

This module encapsulates the hardware-level SoundController to provide 
meaningful audio feedback for race events like finishing, starting, or errors.

Usage:
    from src.functional.race_sounds import RaceSounds

    audio = RaceSounds()
    audio.play_finish_bell()
    audio.cleanup()
"""

from src.core.modules.sound import SoundController

class RaceSounds:
    def __init__(self):
        """
        Initializes the internal SoundController automatically.
        """
        self.controller = SoundController()

    def play_finish_bell(self):
        """The specific 'Ding-Ding-Dinggg' pattern (2300Hz)."""
        config = [
            {'pitch': 2300, 'ms': 192, 'pause': 75}, # Strike 1
            {'pitch': 2300, 'ms': 192, 'pause': 75}, # Strike 2
            {'pitch': 2300, 'ms': 600, 'pause': 0}   # Strike 3 (Sustain)
        ]
        self.controller.play_sequence(config)

    def cleanup(self):
        """Ensures the underlying hardware controller is closed."""
        self.controller.cleanup()