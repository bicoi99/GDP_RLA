from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil

print("Connect to vehicle")
vehicle = connect("127.0.0.1:14551", wait_ready=True)
print("Set ground speed to 0.5 m/s")
vehicle.groundspeed = 0.5
print("Arm vehicle")
vehicle.armed = True
print("Guided mode")
vehicle.mode = VehicleMode("GUIDED")

while True:
    coords = input("\nEnter coordinates (x, y): ")
    if coords == 0:
        print("Exit!")
        break
    print("Go to (%f, %f)" % (coords[0], coords[1]))
    vehicle.simple_goto(LocationGlobalRelative(coords[0], coords[1], 100))
