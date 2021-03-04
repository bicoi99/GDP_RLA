#!/usr/bin/python3

import argparse
from dronekit import LocationGlobalRelative, VehicleMode, connect
import math
from time import sleep
import serial


def _get_distance_metres(lon1, lat1, lon2, lat2):
    """
    Approximate distance (m) from http://www.movable-type.co.uk/scripts/latlong.html
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = math.sin(0.5*dLat)**2 + math.sin(0.5*dLon)**2 * \
        math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    return 6378100.0 * c


def _fetch_mission(vehicle):
    mission = list()
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        mission.append(cmd)
    return mission


if __name__ == "__main__":
    # Get connection string argument
    parser = argparse.ArgumentParser(
        description="Fetch uploaded mission from vehicle and carry out 'guided' motion based on the mission")
    parser.add_argument(
        '--connect',
        help="Connection String, <IP address>:14550"
    )
    args = parser.parse_args()
    connection_string = args.connect
    # Default connection string
    if not connection_string:
        print("No arguments were passed, use 0.0.0.0:14550 as default")
        connection_string = "0.0.0.0:14550"

    # Serial port
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
    sleep(2)

    # Connect to vehicle
    print(f"Connect to vehicle at {connection_string}")
    vehicle = connect(connection_string, wait_ready=True)

    # Check that vehicle is armable to ensures home_location is set
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        sleep(1)

    # Arm vehicle
    vehicle.armed = True

    # Get mission list
    missions = _fetch_mission(vehicle)
    num_missions = len(missions)

    # Loop over all mission
    for mission in missions:
        # Wait for user input
        # input(f"Press 'Enter' to go to waypoint {mission.seq}/{num_missions}")
        # Display target long, lat coord
        print(
            f"Going to waypoint {mission.seq}: ({mission.x:.7f}, {mission.y:.7f})")
        # Create target object
        target = LocationGlobalRelative(mission.x, mission.y, mission.z)
        # Change to guided mode and go to target
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.simple_goto(target)
        # Wait for vehicle to reach location
        while True:
            # Get current distance to target
            distance = _get_distance_metres(
                vehicle.location.global_frame.lon,
                vehicle.location.global_frame.lat,
                target.lon, target.lat
            )
            print(f"Distance to target: {distance:.2f} m")
            # Sleep to avoid excessive pooling
            sleep(0.5)
            # Stopping condition
            if distance < 1:
                # Change to HOLD
                vehicle.mode = VehicleMode("HOLD")
                # Wait for deceleration
                while vehicle.groundspeed > 0.15:
                    print(
                        f"Vehicle is decelerating, current speed: {vehicle.groundspeed:.3f}")
                    sleep(0.5)
                print(
                    f"Waypoint {mission.seq} is reached, current speed: {vehicle.groundspeed:.3f}")
                sleep(2)  # Delay for vehicle to come to complete stop
                print("Signal sent to Arduino to start drilling")
                ser.write(b'1')
                print("Drilling started")
                while True:
                    arduino_msg = ser.read().decode('utf-8')
                    if arduino_msg == '\x01':
                        print("Drilling has finished!")
                        sleep(3)
                        break
                    else:
                        print("Drilling is on-going")
                break
    # Return to launch after all missions have finished
    vehicle.mode = VehicleMode("RTL")
