# Rovers
Welcome, this is the RIT Spex Rover Pi control code. This is the code (as of 4/15/23) that controls the rover.
Depending on the active functions, the pi takes inputs from either a predetermined program or an xbox controller.
It then sends those inputs to an arduino uno which does the actual control of the motors.
On termination, the pi sends instructions to the arduino to disable all motors then reset.
The terminal is designed to give outputs for all connections, signals, and disconnections.

### Included Files
`controlCode.py` - Primary Controlling Script. <br />
`arduino.py` - Package that allows for connection to an arduino. <br />
`fancy.py` - Package that allows for a neater way of printing information. <br />
`serialBridge.ino` - Arm connection. <br />

### Goals
- Interface with the arm
- Add Encoders
- Add Lidar
- Add Camera
- Develop Autonomus Navigation

### Setup
- Please ensure all tools are installed before using this repository:
  - A version of python3, preferably 3.9
  - [Pre-Commit](https://pre-commit.com/) ->
    `python3 -m pip install pre-commit` or `brew install pre-commit`
  - [Poetry](https://python-poetry.org) ->
    `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -`
