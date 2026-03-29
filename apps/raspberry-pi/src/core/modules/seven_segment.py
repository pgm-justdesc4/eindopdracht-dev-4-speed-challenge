"""
seven_segment.py — Generic driver for a 4-digit 7-segment display (common cathode, active-low digits)

Usage:
    from src.core.modules.seven_segment import SevenSegmentDisplay

    display = SevenSegmentDisplay()                  # uses default pins
    display = SevenSegmentDisplay(                   # or override manually
        segment_pins=[19, 5, 24, 20, 21, 13, 22, 26],
        digit_pins=[25, 6, 12, 16],
    )

    display.show("1234")        # 4 individual characters
    display.show("59.23")       # dot is parsed and merged with the preceding character
    display.show("HELO")        # letters where supported by 7-segment rendering
    display.refresh()           # one multiplex cycle — call this in a loop
    display.close()             # clean up GPIO resources
"""

import time
from gpiozero import LED

from src.core.constants.pins import SEGMENT_DIGITS, SEGMENT_PINS

# Segment order: A, B, C, D, E, F, G, DP
CHAR_MAP: dict[str, list[int]] = {
    "0": [1, 1, 1, 1, 1, 1, 0, 0],
    "1": [0, 1, 1, 0, 0, 0, 0, 0],
    "2": [1, 1, 0, 1, 1, 0, 1, 0],
    "3": [1, 1, 1, 1, 0, 0, 1, 0],
    "4": [0, 1, 1, 0, 0, 1, 1, 0],
    "5": [1, 0, 1, 1, 0, 1, 1, 0],
    "6": [1, 0, 1, 1, 1, 1, 1, 0],
    "7": [1, 1, 1, 0, 0, 0, 0, 0],
    "8": [1, 1, 1, 1, 1, 1, 1, 0],
    "9": [1, 1, 1, 1, 0, 1, 1, 0],
    " ": [0, 0, 0, 0, 0, 0, 0, 0],
    "-": [0, 0, 0, 0, 0, 0, 1, 0],
    "A": [1, 1, 1, 0, 1, 1, 1, 0],
    "B": [0, 0, 1, 1, 1, 1, 1, 0],
    "C": [1, 0, 0, 1, 1, 1, 0, 0],
    "D": [0, 1, 1, 1, 1, 0, 1, 0],
    "E": [1, 0, 0, 1, 1, 1, 1, 0],
    "F": [1, 0, 0, 0, 1, 1, 1, 0],
    "G": [1, 0, 1, 1, 1, 1, 0, 0],
    "H": [0, 1, 1, 0, 1, 1, 1, 0],
    "I": [0, 0, 0, 0, 1, 1, 0, 0],
    "J": [0, 1, 1, 1, 1, 0, 0, 0],
    "L": [0, 0, 0, 1, 1, 1, 0, 0],
    "N": [0, 0, 1, 0, 1, 0, 1, 0],  # lowercase 'n' rendering
    "O": [0, 0, 1, 1, 1, 0, 1, 0],  # lowercase 'o' rendering
    "P": [1, 1, 0, 0, 1, 1, 1, 0],
    "R": [0, 0, 0, 0, 1, 0, 1, 0],  # lowercase 'r' rendering
    "S": [1, 0, 1, 1, 0, 1, 1, 0],
    "T": [0, 0, 0, 1, 1, 1, 1, 0],  # lowercase 't' rendering
    "U": [0, 1, 1, 1, 1, 1, 0, 0],
    "Y": [0, 1, 1, 1, 0, 1, 1, 0],
}


def _parse_string(text: str) -> list[tuple[str, bool]]:
    """
    Converts a string into a list of (char, dot) tuples.
    A dot following a character is merged into that character's DP segment.

    "59.23" → [("5", False), ("9", True), ("2", False), ("3", False)]
    "HELO"  → [("H", False), ("E", False), ("L", False), ("O", False)]
    """
    result: list[tuple[str, bool]] = []
    i = 0
    while i < len(text):
        char = text[i].upper()
        dot = False
        if i + 1 < len(text) and text[i + 1] == ".":
            dot = True
            i += 1  # skip the dot character
        result.append((char, dot))
        i += 1
    return result


class SevenSegmentDisplay:
    """
    Generic 4-digit 7-segment display driver.

    Parameters
    ----------
    segment_pins : list[int] | None
        GPIO pin numbers for segments in order A, B, C, D, E, F, G, DP.
        Defaults to SEGMENT_PINS if not provided.
    digit_pins : list[int] | None
        GPIO pin numbers for the 4 digit enables (left to right).
        Defaults to SEGMENT_DIGITS if not provided.
    dwell : float
        Time in seconds each digit stays active per multiplex cycle.
    char_map : dict | None
        Optional custom character map; falls back to the built-in CHAR_MAP.
    """

    def __init__(
        self,
        segment_pins: list[int] | None = None,
        digit_pins: list[int] | None = None,
        dwell: float = 0.001,
        char_map: dict | None = None,
    ):
        self._segments = [LED(p) for p in (segment_pins or SEGMENT_PINS)]
        self._digits = [LED(p, active_high=False, initial_value=True) for p in (digit_pins or SEGMENT_DIGITS)]
        self._dwell = dwell
        self._char_map = char_map or CHAR_MAP
        self._buffer: list[tuple[str, bool]] = [(" ", False)] * 4

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self, text: str) -> None:
        """
        Set what should be displayed.

        Dots in the string are merged with the preceding character's DP segment.
        Maximum 4 characters (not counting dots). Pads with spaces if shorter.

        Examples
        --------
        display.show("1234")   →  1  2  3  4
        display.show("59.23")  →  5  9. 2  3
        display.show(" 9.99")  →     9. 9  9
        display.show("HELO")   →  H  E  L  O
        display.show("ERR ")   →  E  R  R
        """
        parsed = _parse_string(text)
        parsed = parsed[:4]
        while len(parsed) < 4:
            parsed.append((" ", False))
        self._buffer = parsed

    def refresh(self) -> None:
        """
        Run one multiplex cycle (drives all 4 digits once).
        Call this continuously in your main loop to maintain a stable image.
        """
        for i, (char, dot) in enumerate(reversed(self._buffer)):
            pattern = list(self._char_map.get(char, self._char_map.get(" ", [0] * 8)))
            pattern[7] = 1 if dot else 0

            # Turn off all digits
            for d in self._digits:
                d.off()

            # Set segments
            for j, seg in enumerate(self._segments):
                if pattern[j]:
                    seg.on()
                else:
                    seg.off()

            # Enable this digit
            self._digits[i].on()
            time.sleep(self._dwell)

        # Turn everything off at end of cycle to prevent ghosting
        for d in self._digits:
            d.off()

    def close(self) -> None:
        """Release all GPIO resources."""
        for d in self._digits:
            d.close()
        for s in self._segments:
            s.close()

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()