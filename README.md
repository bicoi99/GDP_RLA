# GDP_RLA

This is the GitHub Repository for University of Southampton Group Design Project Robotic Lawn Aerator.

## Table of Contents

- [About](#about)
- [Software In The Loop](#software-in-the-loop)
- [Dronekit](#dronekit)

## Software In The Loop

Here is a guide of how to setup SITL for Linux or Linux Virtual Machine (VM) running on Windows.

### Prerequisites

This assumes some prior knowledge of Python, Linux and Shell scripting.

### Setting up a Linux VM

Follow [this](https://itsfoss.com/install-linux-in-virtualbox/) guide to setup Linux using Oracle VirtualBox.

- You can use any distribution of Linux, but this guide uses Ubuntu 20.04 LTS.
- Ensure you enable SVM in your BIOS (AMD-V for AMD CPUs)

`sudo apt update && sudo apt upgrade` to update everything on your Linux after you finish setting it up following the guide.

### Setup and activating SITL

This is Huy version of the following [guide](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html).

First, you need to setup a build environment for ardupilot. Use [this](https://ardupilot.org/dev/docs/building-setup-linux.html) to setup on Ubuntu. Only follow the first section of the guide i.e. stop before *Setup for other Distributions Using the STM Toolchain* section. Keep a note of where you save ardupilot folder, this is where SITL is going to be activated from.

To start the SITL simulation, you need to select the correct vehicle type. This is done by navigating to the appropriate folder. For RLA, we use Rover firmware so change directory to the correct folder:

```bash
cd ardupilot/Rover
```

The first time SITL gets activated (by running the script `sim_vehicle.py`), it will build itself first which takes 3-5 minutes so be patient (it will only need to build once and subsequent activation will be faster). SITL stores parameters in a virtual EEPROM in the file `eeprom.bin` (can be found in `ardupilot/Rover` directory). So, when you run SITL for the first time you need to wipe this to initiate default params. Use the following command with the flag `-w` to wipe EEPROM:

```bash
../Tools/autotest/sim_vehicle.py -w
```

After the first run, kill the current session with the keyboard interupt `Ctrl+C`. Now you can start the simulation the same way you will do it in any subsequent session by typing into the terminal:

```bash
../Tools/autotest/sim_vehicle.py
```

Now a virtual Rover is simulated on the machine but in order to tap into that virtual vehicle (using MissionPlanner or any GCS for mission planning) you need to use MAVProxy. This is a GCS (Ground Control Station) on its own and you can do a lot of testing with it but it has the ability to forward messages of the vehicle over the network via UDP, meaning you can connect to your simulated Rover using MissionPlanner, the software that RLA mainly uses to calibrate, control the Cube (the real Rover). You can learn more about MAVProxy from the [documentation](https://ardupilot.org/mavproxy/index.html) but here only a few options and commands are required. MAVProxy options can be activated through flags passed to the `sim_vehicle.py` script. Flags can just be typed straight after the script call shown above, many can be used at the same time, just write one after another, so pick and choose your flavour.

The most important one is `-h` this shows all options that `sim_vehicle` can take:

```bash
../Tools/autotest/sim_vehicle.py -h
```

MAVProxy has a builtin map and GUI console that can be activated as follows:

```bash
../Tools/autotest/sim_vehicle.py --map --console
```

SITL initiates at a fixed location (somewhere in the US) and to bring your vehicle to a location of choice, you can use `-L` tag. However, the argument passed has to be the name of the location. You need to make this location in a file found at `ardupilot/Tools/autotest/locations.txt`. The format of this file is each line a location specifed as `NAME=latitude,longitude,absolute-altitude,heading`. Latitude, longitude can be found using Google Maps, absolute-altitude can be any value since Rover ignores altitude and heading is the direction that the vehicle faces at startup. Inside the `sitl` folder of this repository, there is a `locations.txt` file that have the Boldrewood input that you can append to local `locations.txt` file.

```bash
../Tools/autotest/sim_vehicle.py -L <NAME>
```

Now to tackle the MAVProxy capability to forward the vehicle. As default, SITL use MAVProxy to give out 2 outputs `127.0.0.1:14550` and `127.0.0.1:14551` (you can check this by looking at the messages shown after calling `sim_vehicle`). However, unless you have you simulated vehicle and MissionPlanner running on the same machine (not via VM), `localhost` or `127.0.0.1` is not accessible. Rather, the IP address should be used. You need to find the IPv4 Address of your Linux VM by opening the Command Prompt in Windows and type `ipconfig`. Once this is found, the following flags can be used to broadcast to UDP port 14550 (`--no-extra-ports` disable the two default ports which is optional, but I just disable them to avoid any mistakes):

```bash
../Tools/autotest/sim_vehicle.py --no-extra-ports --out <VM-IPv4-Address>:14550
```

In the `sitl` folder of this repo, the `rover-sitl.sh` shell script is available for you to use which automatically turn activate SITL with correct flags when ran. Put this file to the `ardupilot` folder on your Linux VM. Navigate to this folder and type:

```bash
bash rover-sitl.sh
```

Now you can use your simulated Rover either using MissionPlanner by connecting to UDP 14550 or test directly on MAVProxy.

### Using MAVProxy

### Files

- `install-prereqs-mint.sh` is modified script to install prerequisites for Linux Mint 20 (ulyana)
- `locations.txt` file stores the custom location for SITL to start from. This might become uncessary cause the SITL activation script can take care of this on its own
- `rla.parm` is the parmeter file to load in SITL, this only needs to be loaded once because the virtual eeprom can store parms afterwards
- `rover-sitl.sh` is the script to launch SITL from this folder.
- `wsl-rover-sitl.sh` is the script that is previously used inside of Windows WSL

## Dronekit

Communication between the autopilot and the microprocessor that controls the aeration mechanism is not straight forward. The use of a master Raspberry Pi is being investigated and Dronekit is a Python API that allows a companion computer to control the Pixhawk.

Dronekit runs on Python 2 and yet to have support for Python 3 so you need to install this on your system. I recommend Anaconda for easy virtual environment if you run the scripts on you Windows machine. But if you run the script on a VM Linux then you should install Python 2 individually as Anaconda is heavy.
