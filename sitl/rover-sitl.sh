# This script should be ran inside the ardupilot folder

# Go to Rover folder to not have to specify the vehicle type
# Alternatively, can use -v Rover flag but this stores eeprom.bin
# at random location so just keep to this method.
cd Rover

# Run sim_vehicle.py
# Activate map and console
# Start at Boldrewood (change to your location)
# Disable localhost:14550 and 14551
# Broadcast to UDP 14550 of machine (change to the correct VM IP)
../Tools/autotest/sim_vehicle.py --map --console -L Boldrewood \
    --no-extra-port --out <VM-IPv4-Address>:14550
