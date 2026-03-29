"""
src/functional/high_score_lcd.py — High-level LCD controller for race records.

This module provides a specialized interface for the 16x2 LCD, 
standardizing the display of the current high score with consistent 
labels and formatting.

Usage:
    from src.functional.high_score_lcd import HighScoreLCD

    with HighScoreLCD() as hs:
        hs.set("00:45:67")
"""

from src.core.modules.lcd import LCD

LABEL = "== HIGH SCORE =="

class HighScoreLCD:
    def __init__(self, address: int | None = None) -> None:
        self._lcd = LCD(address=address)
        self.clear()

    def set(self, score: str) -> None:
        """
        Update the displayed high score.
        Format:
        Line 1: == HIGH SCORE ==
        Line 2:      00:02.34
        """
        # Center the score on the 16-character wide screen
        centered_score = score.center(16)
        self._lcd.write(line1=LABEL, line2=centered_score)

    def clear(self) -> None:
        """Reset the display to a empty state."""
        self._lcd.write(line1=LABEL, line2="".center(16))

    def close(self) -> None:
        """Closes the underlying LCD hardware connection."""
        self._lcd.close()

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, *_):
        """Ensures hardware cleanup when exiting context."""
        self.close()