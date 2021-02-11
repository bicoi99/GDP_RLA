#! /usr/bin/python

from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil

# Connect vehicle
print("Connect to vehicle")
vehicle = connect("127.0.0.1:14551", wait_ready=True)

# Check arming state
print(vehicle.armed)

# Change vehicle mode
print("Change vehicle mode to Manual")
vehicle.mode = VehicleMode("HOLD")
vehicle.mode = VehicleMode("MANUAL")

# Change vehicle groundspeed
vehicle.groundspeed = 0.5

# Get the set of commands from the vehicle
print("Download commands")
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print("Clear commands")
cmds.clear()

# Create and add commands
print("Add 3 waypoints")
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                 mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 50.9372684, -1.4046249, 100))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                 mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 50.9371561, -1.4046146, 100))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                 mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 50.9371496, -1.4047894, 100))
print("Add RTL")
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                 mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
print("Upload mission")
cmds.upload()  # Send commands

vehicle.armed = True
vehicle.mode = VehicleMode("AUTO")
