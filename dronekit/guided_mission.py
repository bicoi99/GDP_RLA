#!/usr/bin/env python

from __future__ import print_function
from dronekit import connect, Command, LocationGlobalRelative, VehicleMode
from time import sleep
import argparse
import math

# Parse out connection string
parser = argparse.ArgumentParser(
    description="Download from SITL that has been setup by Mission Planner")
parser.add_argument('--connect',
                    help="Vehicle connection, <IP address>:14550")
args = parser.parse_args()
connection_string = args.connect

# If no arguments are passed, use default string to be localhost:14550
if not connection_string:
    print("No arguments were passed, use 127.0.0.1:14550 as default")
    connection_string = "127.0.0.1:14550"

# Connect to vehicle
print("Connecting to vehicle on %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True)

# Check that vehicle is armable.
# This ensures home_location is set (needed when saving WP file)
while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    sleep(1)


# Read mission function
# Use this function to read mission from the waypoint file to load in an example mission.
# In real application this missionlist object is created from downloadmission function instead.
def readmission(aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist = []
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i == 0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray = line.split('\t')
                ln_index = int(linearray[0])
                ln_currentwp = int(linearray[1])
                ln_frame = int(linearray[2])
                ln_command = int(linearray[3])
                ln_param1 = float(linearray[4])
                ln_param2 = float(linearray[5])
                ln_param3 = float(linearray[6])
                ln_param4 = float(linearray[7])
                ln_param5 = float(linearray[8])
                ln_param6 = float(linearray[9])
                ln_param7 = float(linearray[10])
                ln_autocontinue = int(linearray[11].strip())
                cmd = Command(0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue,
                              ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


# Calculate distance (m) from 2 locations
def get_distance_metres(location1, location2):
    """
    Approximate distance (m) from dronekit guide
    """
    dlat = location1.lat - location2.lat
    dlon = location1.lon - location2.lon
    return math.sqrt(dlat**2 + dlon**2) * 1.113195e5


def distance_to_target(target):
    """
    Calculate distance (m) from current location frame to target.
    """
    return get_distance_metres(vehicle.location.global_frame, target)


# Generate missions list from mission1.txt
# Discard first (home) and last (RTL) mission
# missions = readmission("mission1.txt")[1:-1]
missions = readmission("mission_mower.txt")[1:-1]
print("Finish reading, starting the GUIDED motion")
print("Arming the vehicle")
vehicle.armed = True
print("Change mode to GUIDED")
vehicle.mode = VehicleMode("GUIDED")
for mission in missions:
    raw_input("Press Enter to go to next waypoint...")
    print("Going to waypoint %d with coordinates: (%.7f, %.7f)" %
          (mission.seq, mission.x, mission.y))
    target = LocationGlobalRelative(mission.x, mission.y, mission.z)
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.simple_goto(target)
    # sleep(1) # delay for initial acceleration
    while True:
        distance = distance_to_target(target)
        print(distance, vehicle.groundspeed)
        sleep(0.5)
        # if distance < 5 and vehicle.groundspeed < 0.1:
        if distance < 5:
            vehicle.mode = VehicleMode("HOLD")
            while vehicle.groundspeed > 0.1:
                print("Decelerating", vehicle.groundspeed)
                sleep(0.5)
            print("Reached waypoint", vehicle.groundspeed)
            sleep(2)  # Delay to ensure vehicle completely stop
            print("Drilling start")
            break
vehicle.mode = VehicleMode("RTL")

# Need to signal when waypoint is reached
# Need to RTL after finishing, only index missions[1:-1]
