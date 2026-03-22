"""
Serial Client for communicating with Arduino/Firmware
"""
import serial

class SerialClient:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            return True
        except Exception as e:
            print(f"Error connecting to serial: {e}")
            return False

    def send_command(self, cmd):
        if self.ser:
            self.ser.write(f"{cmd}\n".encode())
            return True
        return False

    def read_response(self):
        if self.ser:
            return self.ser.readline().decode().strip()
        return None
