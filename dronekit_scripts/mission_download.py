#!/usr/bin/python

from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
import argparse

parser = argparse.ArgumentParser(
    description="Download from SITL that has been setup by Mission Planner")
parser.add_argument('--connect',
                    help="Vehicle connection, <IP address>:14550")
args = parser.parse_args()
connection_string = args.connect

print("Connecting to vehicle on %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    missionlist = list()
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist


def save_mission(aFileName):
    """
    Save a mission in the Waypoint file format 
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    print("\nSave mission from Vehicle to file: %s" % aFileName)
    # Download mission from vehicle
    missionlist = download_mission()
    # Add file-format information
    output = 'QGC WPL 110\n'
    # Add home location as 0th waypoint
    home = vehicle.home_location
    output += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        0, 1, 0, 16, 0, 0, 0, 0, home.lat, home.lon, home.alt, 1)
    # Add commands
    for cmd in missionlist:
        commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            cmd.seq, cmd.current, cmd.frame, cmd.command, cmd.param1, cmd.param2, cmd.param3, cmd.param4, cmd.x, cmd.y, cmd.z, cmd.autocontinue)
        output += commandline
    with open(aFileName, 'w') as file_:
        print(" Write mission to file")
        file_.write(output)
