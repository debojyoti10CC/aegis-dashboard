
import threading
import serial
import json
import time
import logging
from typing import Optional, Callable, Dict, Any

class SerialBridge:
    """
    Bridges communication between ESP32 hardware via Serial and the Python backend.
    """
    
    def __init__(self, port: str = 'COM3', baud_rate: int = 115200, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize the serial bridge.
        
        Args:
            port: COM port (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate: Serial baud rate (must match ESP32)
            callback: Function to call when valid JSON data is received
        """
        self.port = port
        self.baud_rate = baud_rate
        self.callback = callback
        self.serial_conn = None
        self.running = False
        self.thread = None
        self.logger = logging.getLogger("hardware.serial")
        
    def start(self):
        """Start the serial listener thread"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"Serial bridge started on {self.port}")
        
    def stop(self):
        """Stop the serial listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self._disconnect()
        self.logger.info("Serial bridge stopped")

    def _connect(self) -> bool:
        """Attempt to connect to the serial port"""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                return True
                
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            self.logger.info(f"Connected to ESP32 on {self.port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False

    def _disconnect(self):
        """Close serial connection"""
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except:
                pass
            self.serial_conn = None

    def _listen_loop(self):
        """Main loop for reading serial data"""
        retry_delay = 5
        
        while self.running:
            if not self._connect():
                time.sleep(retry_delay)
                continue
                
            try:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.logger.debug(f"Received raw: {line}")
                        self._process_data(line)
                else:
                    time.sleep(0.1)
                    
            except serial.SerialException as e:
                self.logger.error(f"Serial connection lost: {e}")
                self._disconnect()
                time.sleep(retry_delay)
            except Exception as e:
                self.logger.error(f"Unexpected error in serial loop: {e}")
                time.sleep(1)

    def _process_data(self, data_str: str):
        """Parse JSON data and invoke callback"""
        try:
            # Look for JSON structure start/end if mixed with debug text
            start = data_str.find('{')
            end = data_str.rfind('}')
            
            if start != -1 and end != -1 and end > start:
                json_str = data_str[start:end+1]
                data = json.loads(json_str)
                
                if self.callback:
                    self.callback(data)
            else:
                # Not JSON or partial data
                pass
                
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON: {data_str}")
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
