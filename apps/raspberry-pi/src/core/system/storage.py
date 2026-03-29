"""
src/core/data/storage.py — Local JSON persistence layer for race data.

This module handles reading and writing race results and high scores to 
the local file system, ensuring the storage directory exists.

Usage:
    from src.core.data.storage import Storage

    db = Storage()
    data = db.load("races.json")
    db.save("races.json", [...])
"""

import os
import json

class Storage:
    def __init__(self, relative_path='../../../../../.speed-challenge'):
        # Resolve absolute path based on this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_dir = os.path.abspath(os.path.join(current_dir, relative_path))
        
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def load(self, filename: str) -> list:
        """Reads a JSON file and returns a list. Returns empty list if file missing."""
        filepath = os.path.join(self.storage_dir, filename)
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, filename: str, data: list) -> None:
        """Writes a list of data to a JSON file with indentation."""
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)