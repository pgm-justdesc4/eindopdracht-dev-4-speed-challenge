"""
src/core/button.py — Generic button driver using gpiozero.

Usage:
    from src.core.modules.button import Button

    btn = Button(pin=18)
    btn.on_press(lambda: print("pressed!"))
    btn.close()
"""

from gpiozero import Button as _Button


class Button:
    """
    Generic button driver with debouncing and internal pull-up.

    Parameters
    ----------
    pin : int
        GPIO pin number. Connect the other leg to GND.
    bounce_time : float
        Debounce time in seconds.
    """

    def __init__(self, pin: int, bounce_time: float = 0.05) -> None:
        self._btn = _Button(pin, pull_up=True, bounce_time=bounce_time)

    def on_press(self, callback) -> None:
        """Register a callback to fire when the button is pressed."""
        self._btn.when_pressed = callback

    def on_release(self, callback) -> None:
        """Register a callback to fire when the button is released."""
        self._btn.when_released = callback

    def close(self) -> None:
        """Release GPIO resources."""
        self._btn.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()