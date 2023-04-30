# Rovers
Welcome, this is the RIT Spex Rover Pi Github. This is the code (as of 4/22/23) that controls the rover.
Depending on the active functions, the pi takes inputs from either a predetermined program or an xbox controller.
It then sends those inputs to the pins on the pi and sends a kill code upon termination.
The terminal is designed to give outputs for all connections, signals, and disconnections.

### Included Files
`controlCode.py` - Primary Controlling Script. <br />
`arduino.py` - Package that allows for connection to an arduino. <br />
`fancy.py` - Package that allows for a neater way of printing information. <br />
`pi2UnoTest.py` - Example py script to connect with the teensy. <br />
`simpleGCode.ino` - Arm connection via usb. <br />

### Goals
- Interface with the arm
- Add Encoders
- Add Lidar
- Upgrade to a Crea
- Add Camera
- Develop Autonomus Navigation

### Controls
`Joysticks` - Move corresponding side of wheels (left for left and right for right). <br/>
`Left Bumper` - Reverse controls so that the back of the rover is considered the front. <br/>
`Right Bumper` - Forward controls sot that the front of the rover is the front. <br/>
`Triple Click A` - Swaps between slow and normal speed. <br/>
`X` - Terminates Script

### Colors
`Red and Green` - Script inactive. <br/>
`Red` - Controller not connected. <br/>
`Green` - Code running properly. <br/>
`Blue` - Rover is in reverse so the back is considered the front. <br/>
`Dim Green` - Slow mode active. <br/>

### Setup
- Please ensure all tools are installed before using this repository:
  - #### A version of python3, preferably 3.9
  - #### [Pre-Commit](https://pre-commit.com/) ->
    Windows: `pip install pre-commit` <br />
    Mac: `python3 -m pip install pre-commit` or `brew install pre-commit`
  - #### [Poetry](https://python-poetry.org) ->
    Windows: `Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -OutFile get-poetry.py` <br />
    Mac:  `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -`

### Git Commands:
git clone https://github.com/Ethan-Leone-9134/Rovers.git
git checkout -b new-<new_branch_name>
git commit -m <message here>
