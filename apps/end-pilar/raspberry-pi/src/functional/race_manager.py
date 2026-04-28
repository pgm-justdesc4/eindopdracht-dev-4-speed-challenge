"""
src/functional/race_manager.py — Logic for race data orchestration and high scores.

This module serves as the bridge between raw storage and the race application. 
It manages race lifecycles (start/stop), calculates IDs, and identifies 
the fastest completed records.

Usage:
    from src.functional.race_manager import RaceManager

    manager = RaceManager()
    race_id = manager.start_new_race("2026-03-29T22:00:00Z")
    manager.stop_race(race_id, "2026-03-29T22:00:10Z", 10500)
    print(manager.get_high_score())
"""

from datetime import datetime

from src.core.constants.config import FILE_NAME_RACES
from src.core.system.storage import Storage

class RaceManager:
    def __init__(self):
        self.db = Storage()
        self.filename = FILE_NAME_RACES

    def start_new_race(self, start_time_iso: str) -> int:
        """Creates a new race entry. Returns the generated race ID."""
        races = self.db.load(self.filename)
        new_id = len(races) + 1
        new_race = {
            "id": new_id,
            "started_at": start_time_iso,
            "ended_at": None,
            "time_taken_ms": None
        }
        races.append(new_race)
        self.db.save(self.filename, races)
        return new_id

    def stop_race(self, race_id: int, end_time_iso: str, elapsed_ms: float) -> None:
        """Locates the race by ID and fills in the completion data."""
        races = self.db.load(self.filename)
        for race in races:
            if race["id"] == race_id and race["ended_at"] is None:
                race["ended_at"] = end_time_iso
                race["time_taken_ms"] = int(elapsed_ms)
                break
        self.db.save(self.filename, races)

    def get_high_score(self) -> str:
        """
        Finds the fastest completed race and returns it as a formatted string.
        Returns empty string if no completed races exist.
        """
        races = self.db.load(self.filename)
        
        # Filter only completed races that have a valid time
        completed_races = [r for r in races if r["time_taken_ms"] is not None]
        
        if not completed_races:
            return ""

        # Find the minimum time
        best_race = min(completed_races, key=lambda x: x["time_taken_ms"])
        return self._format_ms_to_lcd(best_race["time_taken_ms"])

    def _format_ms_to_lcd(self, ms: int) -> str:
        """
        Converts milliseconds to a labeled string.
        Example: 2330ms -> 2s 33ms
        """
        total_seconds = ms / 1000.0
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        # Remaining milliseconds (up to 3 digits for precision)
        remainder_ms = int(ms % 1000)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s {remainder_ms}ms"
        return f"{seconds}s {remainder_ms}ms"