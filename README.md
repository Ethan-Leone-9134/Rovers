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
