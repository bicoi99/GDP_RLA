# GDP_RLA

This is the GitHub Repository for University of Southampton Group Design Project Robotic Lawn Aerator.

## Table of Contents

- [About](#about)
- [RLA App](#rla-app)
- [Software In The Loop](#software-in-the-loop)
- [Dronekit](#dronekit)

## About

This repo stores the code and guide for the RLA app, utils scripts for SITL and Raspberry Pi dronekit code. Use the table of contents to navigate to the interested sections

## RLA App

Here is the **installation guide** for the RLA Path Planner.

### Dependencies

There are two dependencies required for the RLA Path Planner:

1. **Python**: you most likely already have Python in your system but if not you can follow [this](https://realpython.com/installing-python/) link to install a new version for any OS. The app is developed in Python 3.8 but you can install any Python 3 version.
2. **Mission Planner**: this application is from Ardupilot and is to be used in conjunction with the RLA app. The latest version can be found along with its installation guide [here](https://ardupilot.org/planner/docs/mission-planner-installation.html).

### Getting the source code

To run the app you need to download the code from the repository. At the top of the page, click the green `Code` button. You can either download the ZIP folder, extract and copy the entire GDP_RLA folder to a place of your choice. Or you can copy the HTTPS link and use git to clone the repo to your wanted location.

![Download Repo](md_img/download_repo.png)

To do the second option, open up Terminal or Command Prompt, navigate to the location you want the code to be in and type: `git clone https://github.com/bicoi99/GDP_RLA.git` and the repo will be automatically cloned to that location. This will require you to have git installed (contact me if you need help) so if you do not want to deal with the hassle, just download ZIP file.

### Python virtual environment (optional)

When using Python, it is good practice to use a virtual environment for every project (find out why [here](https://realpython.com/python-virtual-environments-a-primer/)), so here I will explain how you can do this and setup your virtual environment. This is optional such that you can just as easily use your normal system Python. In that case, just skip this section.

To create a Python virtual environment, open up a Terminal session and navigate to your `Documents` directory (a new folder will be created here to store Python environment so change where you want to make this if you do not want to cluster your Documents folder). Now we will create and go inside a folder (I name this `pyvenv`) to store all our created Python environment by typing:

```bash
mkdir pyvenv && cd pyvenv
```

Now you can create a new environment (I call this `rla`) with:

```bash
python3 -m venv rla
```

If that does not work then try replacing `python3` with `python`. Now a virtual environment is created called `rla` and to activate it, use:

```bash
source rla/bin/activate
```

Now a `(rla)` should appear to the left of your Terminal line and now when you type `python` the version you are using is a brand new empty Python session.

If you have Anaconda installed, creating new environment is explained [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Once you have created and activated your virtual environment, you can proceed to the next step.

### Install required Python packages

Outside of Python itself, there are some dependency packages or library that you need to install. First, navigate using Terminal inside the GDP_RLA folder that you have downloaded above. Type `ls` (for Mac) or `dir` (for Windows) to list out all the files inside the folder and check with the GitHub page that you have all the relevant files and folders including `requirements.txt` file. Next, you can install all required Python libraries for the RLA app with the command:

```bash
pip install -r requirements.txt
```

After the automatic install is completed, you will have installed: `matplotlib` (`numpy` along with it) and `dronekit`.

### Running the app

Now you are ready to run the app, just type:

```bash
python rla_app.py
```

Now the app is ready to be used and the order of operation is shown in next section.

### Using the app

Open Mission Planner software to the PLAN tab and navigate the map to a random location of your choice (I use Boldrewood as an example).

![MP Plan Tab](md_img/MP_plan_tab.png)

Right click on the map and select `Polygon > Draw a Polygon`.

![MP Draw Polygon](md_img/MP_draw_polygon.png)

Left click on the map to assign polygon verticies/corners. You can drag to change position. Right click on a polygon and `Delete WP` to delete an unwanted vertex.

![MP Polygon](md_img/MP_polygon.png)

Right click and and select `Polygon > Save Polygon`. Save the .poly file to the location stated in the RLA app start screen (inside GDP_RLA/rla_app_files folder with the name `lawn-polygon.poly` as default but you can change it if you like).

![MP Save Polygon](md_img/MP_save_polygon.png)

Now follow the app and it should guide you along the process to generate a "lawnmower" path from the polygon file you have created. If you spot anything that is unclear, let me know so I can improve it.

After you have generated the path file, go back to Mission Planner and press `Load File` on the right hand side. Load the file that you saved in RLA app (default is `polygon-path.txt` in the same folder as `lawn-polygon.poly`).

![MP Load File](md_img/MP_load_file.png)

The correct path should be loaded into Mission Planner. From here you can proceed as if it is a normal mission.

![MP Loaded Mission](md_img/MP_loaded_mission.png)

### Report bugs

The app is still under development so please do come back to me if you find any bugs at all.

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
