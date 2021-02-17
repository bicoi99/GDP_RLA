#!/usr/bin/bash

# SITL startup script for use of Raspberry Pi. Disable all
# local broadcast and only broadcast to RPi IP.

# Get CWD
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Check Ardupilot is present
ARDUPILOT_DIR="$( cd $SCRIPT_DIR/../.. && pwd )/ardupilot"
if ! [ -d $ARDUPILOT_DIR ]; then
    echo "No ArduPilot directory found!"
    exit 1
fi

# SITL
# Custom location
CUSTOM_LOCATION="$( cat $SCRIPT_DIR/locations.txt | cut -d"=" -f2)"
# Go to Rover
cd $ARDUPILOT_DIR/Rover
# Start SITL with no local output and only RPi output
# RPi IP stored in environment variable already
sim_vehicle.py --map --console --custom-location=$CUSTOM_LOCATION \
    --no-extra-ports --out=$RPiIP:14550