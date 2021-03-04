# This script test serial communication between RPi/Linux computer and Arduino.
# The Arduino script serial_comm.cpp in lib/serial_comm is used to intepret
# sent data. Now it is only a simple turning on of the builtin LED.

import serial
from time import sleep

ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
sleep(2)

# Send a single 1 to turn on LED and start drilling. 1 must be a 1 byte string
ser.write(b'1')
print("Drilling has started")

# Receive info from Arduino and print out. Break out of loop when signal 1 is
# sent back from Arduino indicating drilling has finished
while True:
    arduino_msg = ser.read().decode('utf-8')
    if arduino_msg == '\x01':
        print("Drilling has finished!")
        break
    else:
        print("Drilling is on-going")
