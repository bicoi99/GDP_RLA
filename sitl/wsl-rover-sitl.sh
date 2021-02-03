#!/usr/bin/env bash

# The script will go to Rover inside ardupilot and start up SITL
# then it will forward the signal to the IP of RaspberryPi and 
# computer

# Go to Rover folder
cd ardupilot/Rover

# Get IP address of WSL to broadcast to computer for MissionPlanner to connect to. Use grep to get the nameserver role in resolve.conf, then use awk to print out the second column. Append the port 14550 to the end and store the string into variable wslIP.
# To use commands inside string, use $() 
wslIP="$(grep nameserver /etc/resolv.conf | awk '{print $2}'):14550"

# Raspberry Pi IP
rpiIP="10.177.138.32:14550"

../Tools/autotest/sim_vehicle.py -L Boldrewood --map --console \
	--out $wslIP --out $rpiIP # use variable wslIP and rpiIP here
