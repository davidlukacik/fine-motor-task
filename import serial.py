import serial
import time
import subprocess

# Set up serial communication with Arduino
ser = serial.Serial('COM4', 9600, timeout=1)

# Wait for Arduino to initialize
time.sleep(2)

while True:
    # Read incoming data from serial port
    data = ser.readline().decode().strip()
    
    # If data is "Trial started", activate camera
    if data == "Trial started":
        # Activate camera for 30 seconds
        subprocess.call(["spinview.exe", "-capture", "-duration", "30"])
