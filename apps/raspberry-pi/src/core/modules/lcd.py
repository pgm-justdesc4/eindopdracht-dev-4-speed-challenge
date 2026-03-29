"""
src/core/lcd.py — Generic driver for a 16x2 HD44780 LCD via I2C backpack.

Requires:
    pip install RPLCD smbus2

Usage:
    from src.core.lcd import LCD

    lcd = LCD()
    lcd.write("Hello", "World")
    lcd.clear()
    lcd.close()
"""

from RPLCD.i2c import CharLCD

KNOWN_ADDRESSES = [0x27, 0x3F]
I2C_BUS = 1
COLS = 16
ROWS = 2


def _detect_address() -> int:
    """Try known I2C addresses and return the first that responds."""
    import smbus2
    bus = smbus2.SMBus(I2C_BUS)
    for addr in KNOWN_ADDRESSES:
        try:
            bus.read_byte(addr)
            bus.close()
            print(f"[LCD] Found at I2C address 0x{addr:02X}")
            return addr
        except OSError:
            continue
    bus.close()
    raise RuntimeError(
        f"[LCD] No LCD found at {[hex(a) for a in KNOWN_ADDRESSES]}. "
        "Run 'i2cdetect -y 1' to check the correct address."
    )


class LCD:
    """
    Generic 16x2 LCD driver.
    Only writes to the display when content actually changes, preventing flicker.

    Parameters
    ----------
    address : int | None
        I2C address of the backpack. Auto-detected if None.
    """

    def __init__(self, address: int | None = None) -> None:
        addr = address or _detect_address()
        self._lcd = CharLCD(
            i2c_expander="PCF8574",
            address=addr,
            port=I2C_BUS,
            cols=COLS,
            rows=ROWS,
            dotsize=8,
        )
        self._current: tuple[str, str] = ("", "")
        self._lcd.clear()

    def write(self, line1: str = "", line2: str = "") -> None:
        """
        Write two lines to the display.
        Only updates the display if the content has changed.
        Each line is padded or truncated to 16 characters.
        """
        l1 = self._fmt(line1)
        l2 = self._fmt(line2)

        if (l1, l2) == self._current:
            return  # nothing changed, skip write to prevent flicker

        self._current = (l1, l2)
        self._lcd.home()
        self._lcd.write_string(l1)
        self._lcd.crlf()
        self._lcd.write_string(l2)

    def clear(self) -> None:
        """Clear the display."""
        self._current = ("", "")
        self._lcd.clear()

    def close(self) -> None:
        """Clear and release the display."""
        self._lcd.close(clear=True)

    def _fmt(self, text: str) -> str:
        return text[:COLS].ljust(COLS)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()