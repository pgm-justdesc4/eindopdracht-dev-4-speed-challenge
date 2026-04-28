"""
src/core/networking/socket_io.py — Serial bridge for ESP32 communication.

This module listens to the Serial port (USB) for events sent by the ESP32,
mimicking the previous Socket.IO behavior to ensure compatibility with main.py.
"""

import serial
import threading
import json
import time

class SocketClient:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        self._thread = None
        
        # Mimic the python-socketio 'sio' object to avoid breaking main.py
        self.sio = type('MockSIO', (), {'on': self._register_callback, 'emit': self._mock_emit})()
        self.callbacks = {}

    def _register_callback(self, event_name):
        """Decorator replacement for @client.sio.on(event)"""
        def decorator(f):
            self.callbacks[event_name] = f
            return f
        return decorator

    def _mock_emit(self, event, data):
        """Optional: send data back to ESP32 if needed"""
        if self.serial_conn and self.serial_conn.is_open:
            message = f"SEND:{event}:{json.dumps(data)}\n"
            self.serial_conn.write(message.encode('utf-8'))

    def connect(self):
        """Initialize the Serial connection and start the background listener."""
        try:
            # Op Raspberry Pi is de ESP32 meestal /dev/ttyUSB0 of /dev/ttyACM0
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            print(f"[Serial] Connected to ESP32 on {self.port}")
            return True
        except Exception as e:
            print(f"[Serial] Error connecting to ESP32: {e}")
            return False

    def _read_loop(self):
        """Background thread that parses Serial data from the ESP32."""
        while self.running:
            if self.serial_conn and self.serial_conn.in_waiting > 0:
                try:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line.startswith("DATA:"):
                        # Formaat ESP32: DATA:["event_name", {"payload": "data"}]
                        raw_json = line[5:] 
                        data_list = json.loads(raw_json)
                        
                        if isinstance(data_list, list) and len(data_list) >= 1:
                            event_name = data_list[0]
                            payload = data_list[1] if len(data_list) > 1 else None
                            
                            if event_name in self.callbacks:
                                self.callbacks[event_name](payload)

                    elif line == "SYSTEM:CONNECTED":
                        print("\n[ESP32] Socket.IO Connected")
                    elif line == "SYSTEM:DISCONNECTED":
                        print("\n[ESP32] Socket.IO Disconnected")
                        
                except Exception as e:
                    print(f"[Serial] Read error: {e}")
            
            time.sleep(0.01)

    def disconnect(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        print("[Serial] Disconnected.")