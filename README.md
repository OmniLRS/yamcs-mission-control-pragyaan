# OmniLRS - Yamcs Mission Control - Pragyaan Rover

**Mission Control System for the OmniLRS lunar rover simulator**

It is configured for the Pragyaan Rover reference mission, as defined in the December 2025 workshop organized by JAOPS in Tokyo. For more information on the workshop and relevant context, see [here](https://www.jaops.com/events/yamcs-grafana-and-lunar-simulator-workshop)

The Yamcs Mission Control System connects the target devices (from the flight model Rover on the Moon to individual engineering model components being tested) to end-users (from operators in the Mission Control Center to engineers developing hardware).
It provides a robust framework already proven in lunar rover missions and selected by space agencies to accelerate development and safely operate missions. 

The Yamcs Mission DataBase (MDB) serves as the single source of truth for all telemetry and telecommands. 
This provides a well defined interface between every system that needs to receive or transmit data from and to the rover. 
It is version controlled in this repository.
Every data from every test is stored in Yamcs archives and can be easily accessed via the Yamcs python client.

- The `mdb` folder provides the python scripts to generate the MDB. The MDB will grow iteratively as the rover designs progresses. 
- The `tmtc_mock` folder provides script for generating mock telemetry and images and receiving telecomands from Yamcs.
- The `yamcs-server` folder provides the configuration of Yamcs for this specific project.

Get started with the instructions below:

## Prerequisites
1. Java 17+ is required to run Yamcs
```bash
sudo apt install openjdk-25-jdk  # java 25
```

2. Create a virtual environment for the Yamcs python client etc

```bash
python3 -m venv .venv/workshop
source .venv/workshop/bin/activate
pip3 install -r requirements.txt
```

## Common Commands

1. (re)generate the Mission DataBase
```bash
python3 mdb/generate_mdb_rover.py
python3 mdb/generate_mdb_lander.py
python3 mdb/generate_mdb_admin.py
```
Outputs the XTCE XML files to `yamcs-server/src/main/yamcs/mdb/`.

2. Run the Yamcs Server

```bash
cd yamcs-server
./mvnw yamcs:run
```
Starts Yamcs Web on http://localhost:8090 with instance `workshop`.

3. Run TMTC Mocks

In separate terminals (with the venv activated):

```bash
# Telemetry simulator (1 Hz sinusoidal parameters) -> see values update in Yamcs Web / Telemetry / Parameters
python3 tmtc_mock/telemetry/generate_tm.py

# Streaming images (low-res, every 5s) -> see images in Yamcs web / Storage / Preview Panel
python3 tmtc_mock/images/generate_image_stream.py

# On-command images (listens for telecommands from Yamcs and generates hi-res camera images)
# Send commands via Yamcs Web / Commanding / Send a Command / Rover / camera / camera_capture_high 
python3 tmtc_mock/images/generate_image_oncommand.py
```

## Documentation

[Yamcs documentation](https://docs.yamcs.org/)

[Yamcs - OmniLRS interface documentation in the Wiki - coming soon](https://github.com/OmniLRS/OmniLRS/wiki)
