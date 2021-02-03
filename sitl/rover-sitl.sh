#!/usr/bin/env bash

# Check ardupilot is present in ../.. same layer as GDP_RLA
# Use custom location rather than edit locations.txt
# Option to use RPi

# Check current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "This script is run in the directory: $SCRIPT_DIR"

# Check if ardupilot is present in same layer as GDP_RLA
ARDUPILOT_DIR="$( cd $SCRIPT_DIR/../.. && pwd )/ardupilot"
if [ -d $ARDUPILOT_DIR ]; then
	echo "$ARDUPILOT_DIR exists. SITL can start."
else
	echo "No ardupilot is found. Please clone this!"
	exit 1
fi

# SITL
# Get custom location from locations.txt
CUSTOM_LOCATION="$( cat $SCRIPT_DIR/locations.txt | cut -d"=" -f2)"
# Go to Rover
cd $ARDUPILOT_DIR/Rover
# Start SITL with map console and a custom location
sim_vehicle.py --map --console --custom-location=$CUSTOM_LOCATION
