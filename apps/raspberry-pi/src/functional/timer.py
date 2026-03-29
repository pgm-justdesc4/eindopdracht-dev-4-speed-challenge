"""
src/functional/timer.py — Race timer with integrated 7-segment display logic.

This module manages the timing state machine (start/stop/reset) and 
handles the conversion of floating-point seconds into human-readable 
multiplexed strings for the 7-segment display.

Usage:
    from src.functional.timer import RaceTimer

    with RaceTimer() as timer:
        timer.start()
        while timer.running:
            timer.refresh()
"""

import time
from src.core.modules.seven_segment import SevenSegmentDisplay


class RaceTimer:
    """
    Race timer with integrated 7-segment display control.

    State machine:
        stopped  ──start()──▶  running  ──stop()──▶  stopped
           ▲                                            │
           └───────────────reset()──────────────────────┘
    """

    def __init__(self) -> None:
        self._display = SevenSegmentDisplay()
        self._start_time: float | None = None
        self._last_stop_time: float | None = None
        self._elapsed: float = 0.0
        self._running: bool = False

        self._show_startup()

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Start the timer from 0.0 ONLY if it is currently stopped.
        If already running, this method does nothing and returns False.
        """
        if self._running:
            return False

        self._elapsed = 0.0
        self._start_time = time.time()
        self._last_stop_time = None
        self._running = True
        return True

    def stop(self) -> bool:
        """
        Stop the timer if it is running.
        Returns True if successfully stopped, False if it was already stopped.
        """
        if self._running:
            self._elapsed = time.time() - self._start_time
            self._last_stop_time = time.time()
            self._running = False
            return True
        return False

    def reset(self) -> None:
        """Reset the timer to 00.00 and stop it."""
        self._start_time = None
        self._elapsed = 0.0
        self._running = False
        self._last_stop_time = None
        self._display.show("00.00")

    def refresh(self) -> None:
        """
        Run one multiplex cycle. Call this continuously in your main loop.
        Updates the display string only when running.
        """
        if self._running:
            self._display.show(self._elapsed_to_display())

        elif self._last_stop_time is not None:
            if (time.time() - self._last_stop_time) > 60:
                self.reset()

        self._display.refresh()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._running

    @property
    def elapsed(self) -> float:
        """Current elapsed time in seconds."""
        if self._running:
            return time.time() - self._start_time
        return self._elapsed

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _elapsed_to_display(self) -> str:
        """
        Convert elapsed seconds to a display string.
        0 – 99.99s -> SS.hh | 100 – 999.9s -> SSS.h | 1000+ -> SSSS
        """
        t = self.elapsed

        if t >= 9999:
            t = t % 9999

        if t < 100:
            secs = int(t)
            hundredths = int((t * 100) % 100)
            return f"{secs:2d}.{hundredths:02d}"
        elif t < 1000:
            secs = int(t)
            tenths = int((t * 10) % 10)
            return f"{secs:3d}.{tenths}"
        else:
            return f"{int(t):4d}"

    def _show_startup(self) -> None:
        for msg in ["----", "    ", "00.00"]:
            self._display.show(msg)
            for _ in range(100):
                self._display.refresh()

    # ------------------------------------------------------------------
    # Context manager / cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._display.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()