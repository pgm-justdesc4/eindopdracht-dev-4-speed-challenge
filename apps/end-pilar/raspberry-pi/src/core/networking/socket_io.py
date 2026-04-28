"""
src/core/networking/socket_io.py — Socket.IO client for real-time server communication.

This module handles the persistent connection to the race server, including 
automatic reconnection logic and background event processing.

Requires:
    pip install "python-socketio[client]"

Usage:
    from src.core.networking.socket_io import SocketClient

    client = SocketClient()
    client.connect()
    
    client.sio.emit("event_name", {"data": "value"})
    
    client.sio.on("server_event", callback_function)
    def callback_function(data):
        print("Received data:", data)
    
    client.disconnect()
"""

import socketio

from src.core.constants.config import SOCKET_SERVER_URL

class SocketClient:
    def __init__(self):
        self.server_url = SOCKET_SERVER_URL
        self.sio = socketio.Client(
            reconnection=True, 
            reconnection_attempts=0, 
            reconnection_delay=5
        )
        self._setup_internal_events()

    def _setup_internal_events(self):
        """Sets up the event listeners for connection status."""
        @self.sio.event
        def connect():
            print("\n[SocketIO] Connected to server!")
            print("> ", end="", flush=True)

        @self.sio.event
        def disconnect():
            print("\n[SocketIO] Disconnected from server!")
            print("> ", end="", flush=True)

    def connect(self):
        """Start the connection and the background thread (prevents packet queue errors)."""
        try:
            self.sio.connect(self.server_url, transports=['websocket'])
            self.sio.start_background_task(self.sio.wait)
            return True
        except Exception as e:
            print(f"[SocketIO] Error connecting: {e}")
            return False

    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()