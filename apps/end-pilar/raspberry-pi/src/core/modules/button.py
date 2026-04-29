from gpiozero import Button as _Button, PWMLED
from typing import Optional, Callable


class Button:
    def __init__(self, btn_pin: int, led_pin: int = 17, bounce_time: float = 0.05) -> None:
        self._btn = _Button(btn_pin, pull_up=True, bounce_time=bounce_time)
        
        # Door active_high=False te zetten, begrijpt gpiozero dat 
        # 0V 'aan' is en 3.3V 'uit' is.
        self._led = PWMLED(led_pin, active_high=False)
        
        self.set_led_state(0)

    def set_led_state(self, state: int) -> None:
        """
        Set the LED to one of three states: 0=Off, 1=On, 2=Pulse.
        """
        self._led.off() 
        
        if state == 0:
            pass
        elif state == 1:
            self._led.on()
        elif state == 2:
            self._led.pulse(fade_in_time=1, fade_out_time=1, background=True)
        else:
            raise ValueError("State must be 0, 1, or 2")

    def on_press(self, callback: Callable) -> None:
        self._btn.when_pressed = callback

    def on_release(self, callback: Callable) -> None:
        self._btn.when_released = callback

    def close(self) -> None:
        self._btn.close()
        self._led.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()