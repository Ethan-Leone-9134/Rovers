# !/usr/bin/env python3
# -- coding: utf-8 -*-

# NOTE: Do not remove above code, it tells the pi what coding language is being used!

# Welcome, this is the RIT Spex Rover Pi control code. This is the code (as of 4/2/23) that controls the rover.
# Depending on the active functions. The pi takes inputs from either a predetermined program or an xbox controller.
# It then sends those inputs to an arduino uno which does the actual control of the motors.
# On termination, the pi sends instructions to the arduino to disable all motors then reset.
# The terminal is designed to give outputs for all connections, signals, and disconnections.

# %% Start Imports ###
import os  # Additional python and pi interface
import sys  # Used to track terminal output
import time  # Allows to pause

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'  # Disable pygame welcome message
import pygame  # Interfaces with xbox controller
import atexit  # "At Exit" module for when code is terminated
import serial as ser  # Interfaces with the arduino
import RPi.GPIO as GPIO  # Used for controlling the motors from the pi
import math  # Additional math functions
import signal  # Used to control keyboard interrupt

### End imports ###

# %% Start Formatting ###
pygame.init()  # Initializes pygame
os.putenv('SDL_VIDEODRIVER', 'dummy')  # Disable digital display


### End Formatting ###

# %%####### Start Custom Functions ##########

### Directory ###
# Arduino   - Functions that interface with the arduino
# formSerialConnection  - Connects to the arduino
# resetArduino          - Disables all motors and refresh the arduino (Takes 2.6 seconds of pause)
# setDuty               - Tells the arduino to set a motor to a duty cycle
# Inputs    - Loops with pre-defined inputs
# presetInputProgram    - Change speeds for motors from front to off to back to off
# manualInputs          - Takes input from terminal
# xBox      - Functions that interface with the xBox controller
# wait4XboxController   - Loop that runs until the xbox controller has been connected
# receiveXboxSignals    - Process data sent from the xbox controller
# calcDutyCycle         - Converts [-1, 1] range to duty cycle
# buttonPressEvent      - Command for button presses
# GPIO      - Functions for pi control of motors
# initializeGPIO        - Create the GPIO motor objects
# General   - Miscellaneous Functions
# cleanup               - Function that runs on termination of code
# startPrintTracking    - Allows code to track all outputs to command window in a text file
# fancyPrint            - Prints output in a formatted way with dashes for significant information


# %% Start Arduino Function ###


def formSerialConnection():
    # Function to establish a connection with the arduino via usb cable
    # Inputs  : none
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino

    global uno  # Serial communication variable

    while True:  # Loop until connected
        try:
            uno = ser.Serial('/dev/ttyACM0', 115200, timeout=0.1)  # Enable arduino communication (pi)
            # uno = ser.Serial('COM5', 115200, timeout=.1)                # Enable arduino communication (laptop)
        except:
            print("ERROR : Arudino not connected to Pi")  # Warn about an improper connection
            time.sleep(1)  # Delay between pings
        else:
            time.sleep(1.8)  # Delay to allow connection to solidify
            fancyPrint("Arduino Connection Is Established")  # Inform about the connection
            break  # End the loop


def resetArduino():
    # Function reset the connected arduino and gives a 2-second delay to allow the arduino to finish resetting
    # Inputs  : none
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino

    global uno

    for pin in [1, 4, 2, 5, 3, 6]:  # Repeat for each pin from front to back
        setDuty(pin, 30)  # Disable motor
    fancyPrint("All Motors Should Be Off")
    time.sleep(0.5)  # Pause for motors to stop
    uno.setDTR(False)  # Set active to false
    time.sleep(0.1)  # Give it 1/10 second to process
    uno.setDTR(True)  # Set active to true
    time.sleep(2)  # Allow uno to setup and start


def setDuty(motorCode, dutyCycle):
    # Tells the arduino to change a motor's duty cycle
    # Inputs  : motorCode - number of motor to be change [(1-3) - Left]   [(4-6) - Right]
    #           dutyCycle - target duty cycle to set motor to
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino
    # Example : setDuty(1, 20) - Sets Front Left motor to 20

    global uno

    output = motorCode * 100 + dutyCycle  # Create output value
    try:
        uno.write(str(output).encode())  # Transmitts data
    except:
        print("Arduino is no longer connected !!!")  # Warn disconnection
        formSerialConnection()  # Reconnect arduino
    else:
        noResponse = 1  # Logical variable to know if the arduino has returned a response
        while noResponse:
            data = uno.readline()  # Read the serial monitor
            if data:
                rawData = data.rstrip('\n'.encode('latin-1'))  # Convert monitor to bytes
                print("Arduino: " + rawData.decode('latin-1'))  # Print data
                noResponse = 0  # Let code progress


### End Arduino Functions ###


# %% Start Input Programs ###


def presetInputProgram():
    # Loop to Verify Outputs: Runs through each speed type for motors
    # Inputs  : none
    # Outputs : none
    # Globals : none

    while True:
        # 20% - Full Reverse    =       Rover Goes forwards
        # 30% - Stopped         =       Rover is not moving
        # 40% - Full Forward    =       Rover goes backwards

        dutyLeft = 30  # Initialize left duty cycle

        for i in [-1, 0, 1, 0]:  # Run loop for the values [-1,0,1,0]
            currMotor = 2  # Set duration of ramp cycle
            i = 0  # Overwrite for a constant off duty cycle
            while currMotor > 0:
                dutyLeft = calcDutyCycle(i)  # Calculate duty cycle
                print("Python: Set the duty percentage to {}.".format(
                    dutyLeft))  # Tell user what the pi is telling arduino
                setDuty(currMotor + 3, 20)  # Set duty cycle
                currMotor = currMotor - 1
                time.sleep(2)
                print(" ")


def manualInputs():
    # Function takes an input of a pincode and a dutycycle from the terminal
    # Inputs  : none
    # Outputs : none
    # Globals : none

    pin = int(input("What pin code (1-6)? "))  # Get pin code
    duty = int(input("What duty cycle ? "))  # Get duty cycle
    setDuty(pin, duty)  # Set value


# %% Start xBox Functinos

def wait4XboxController():
    # Function to delay program until x-box controller is connected
    # Inputs  : none
    # Outputs : none
    # Globals : none

    pygame.init()  # Initializes pygame
    pygame.joystick.init()  # Initialize joystick data

    # Check if there are any joysticks already connected
    if pygame.joystick.get_count() > 0:  # If a joystick has been connected
        controller = pygame.joystick.Joystick(0)  # Create controller variable
        controller.init()  # Initialize controller
        fancyPrint("The {} is connected".format(controller.get_name()))
        return controller  # Return variable

    # If no joysticks are connected, wait for one to be added
    while True:
        for event in pygame.event.get():  # Handle pygame events
            if event.type == pygame.JOYDEVICEADDED:  # If a joystick is connected
                controller = pygame.joystick.Joystick(0)  # Create controller variable
                controller.init()  # Initialize controller
                fancyPrint("The {} is connected".format(controller.get_name()))
                return controller  # Return the initialized controller object
        print("Retrying controller connection...")  # Take a guess...
        time.sleep(2)  # Two-second delay


def receiveXboxSignals(cont):
    # Function to direct all data from the x-box controller
    # Inputs  : none
    # Outputs : none
    # Globals : none

    # Check for joystick events
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:  # Code for button press  # NOTE: MAPPING NEEDS VERIFICATION
            buttonPressEvent(event)

        if event.type == pygame.JOYAXISMOTION:  # Code for joystick motion
            if event.joy == 0:  # If left joystick
                if event.axis == 0:  # If x-axis
                    pass
                elif event.axis == 1:  # If y-axis
                    print(event.value)
                    dutyLeft = calcDutyCycle(event.value)
                    setDuty(4, round(dutyLeft))
                    print(dutyLeft)
            elif event.joy == 1:  # If right joystick
                if event.axis == 2:  # If x-axis
                    pass
                elif event.axis == 3:  # If y-axis
                    dutyRight = calcDutyCycle(event.value)
                    setDuty(4, dutyRight)
                    print(dutyRight)
        time.sleep(0.05)


def calcDutyCycle(signal):
    # Function to set the new value of the duty cycle from xbox controller
    # Inputs  : signal - xbox joystick value (event.value)
    # Outputs : duty   - value of updated duty cycle
    # Globals : none
    #
    # 20% - Full Reverse    =       Rover Goes forwards
    # 30% - Stopped         =       Rover is not moving
    # 40% - Full Forward    =       Rover goes backwards
    #
    # Left Xbox Joystick Axis Notes:
    # Axis 0 - Up/Down      -   Down value is -1    Up value is 1
    # Axis 1 - Left/Right   -   Left value is -1    Right value is 1
    # Center is always 0
    # For Right Joystick axes are 2,3

    offset = 30  # Neutral dutyCycle
    if (signal >= -0.01) and (signal <= 0.09):  # If joysticks are likely untouched
        duty = offset  # Prevent motion
    else:  # If signal seems intentional
        duty = -10 * signal + offset  # Run Conversion algorithm for joystick to dutyCycle
    return duty


def buttonPressEvent(event):
    # Function for whenever an xbox button is pressed
    # Inputs  : event - event of button press
    # Outputs : none
    # Globals : none

    if event.button == 11:  # Middle Right "Menu" Button
        print("button 11 down")
        os.system("systemctl poweroff")  # Instantly kill script
    elif event.button == 0:  # "A" Button
        print("button 0 down")
    elif event.button == 1:  # "B" Button
        print("button 1 down")
    elif event.button == 2:  #
        print("button 2 down")
    elif event.button == 3:  # "X" Button
        print("button 3 down")
        resetArduino()
    elif event.button == 4:  # "Y" Button
        print("button 4 down")
    elif event.button == 5:
        print("button 5 down")
    elif event.button == 6:  # Left Bumper
        print("button 6 down")
    elif event.button == 7:  # Right Bumper
        print("button 7 down")
    elif event.button == 8:  # Left joystick button
        print("button 8 down")
    elif event.button == 9:  # Right joystick button
        print("button 9 down")
    elif event.button == 10:  # XBOX button
        print("button 10 down")


### End xBox Functions

# %% Start GPIO Functions ###

def initializeGPIO():
    # Initializes all GPIO motor pins
    # Inputs  : none
    # Outputs : leftMotor   - PWM pin for the left  motor controls
    #           rightMotor  - PWM pin for the right motor controls
    # Globals : none

    offset = 30  # No motion duty cycle
    cycle = 30  # Duty cycle info
    freq = 200  # Duty cycle frequency

    ### Initializes Pinmodes for the pi controls
    leftMotorPin = 12  # Set left motor pins
    rightMotorPin = 13  # Set right motor pins
    GPIO.setwarnings(False)  # Disable GPIO warnings
    GPIO.setmode(GPIO.BCM)  # Change GPIO Mode
    GPIO.setup(leftMotorPin, GPIO.OUT)  # GPIO Setups for left motor
    GPIO.setup(rightMotorPin, GPIO.OUT)  # GPIO Setups for right motor

    leftMotor0 = GPIO.PWM(leftMotorPin, freq)  # Activate PWM Signals for left motors
    leftMotor0.start(0)

    rightMotor0 = GPIO.PWM(rightMotorPin, freq)  # Activate PWM Signals for right motors
    rightMotor0.start(0)

    return [leftMotor0, rightMotor0]


# %% Start General Functions ###


def cleanup():
    # Callback function to disable the motors attached to the arduino
    # Inputs  : none
    # Outputs : none
    # Globals : uno     -   Calls the arduino communication variable

    global uno
    if uno is not None:  # If there is a connection
        try:
            resetArduino()  # Restart arduino
            uno.close()  # End arduino communication
        except:
            pass
        else:
            fancyPrint("Arduino Disconnected")  # Inform of disconnection

    fancyPrint("Program Terminated")  # Inform of termination


def startPrintTracking():
    # Function enables tracking of the terminal output
    # Inputs  : none
    # Outputs : none
    # Globals : none

    # Note: Code came from ChatGPT

    class Tee:
        """
        Tee object that captures output to both stdout and a file.
        """

        def __init__(self, filename, stream):
            self.file = open(filename, 'a')
            self.stream = stream

        def __del__(self):
            self.file.close()

        def write(self, data):
            self.file.write(data)
            self.file.flush()
            self.stream.write(data)

        def flush(self):
            self.file.flush()
            self.stream.flush()

    # Define the log file path
    log_file_path = "/home/spex/Desktop/outputLogs.txt"

    # Create a file object for the log file
    log_file = open(log_file_path, 'w')

    # Create a Tee object to capture output to both stdout and the log file
    tee = sys.stdout = Tee(log_file_path, sys.stdout)


def fancyPrint(inputText):
    # Provides formatted output for important information
    # Inputs  : none
    # Outputs : none
    # Globals : none

    dashLen = 50  # Number of dashes
    breakLine = "-" * dashLen  # Create the breakline
    with open("/home/spex/Desktop/outputLogs.txt", 'r') as f:  # Open the log file
        lines = f.readlines()  # Read the last line
        if "-------" not in lines[-1].strip():  # If there was no breakline above
            print(breakLine)  # Add a breakline
        textLength = len(inputText)  # Length of input
        sides = math.floor((dashLen - textLength - 2) / 2)  # Finds amount of side dashes
        sides = '-' * sides  # Generates side walls
        if textLength % 2 == 0:  # If text length is even
            print(sides + " " + inputText + " " + sides)  # Normal formatted print
        else:  # If text length is odd
            print(sides + " " + inputText + " -" + sides)  # Formatted print with an extra dash
        print(breakLine)  # Print ending breakline


def handleInterrupt(signum, frame):
    # Modifies the keyboardInterupt Event
    # Inputs  : none
    # Outputs : none
    # Globals : none

    print('\n')  # Better looks
    fancyPrint("!!! Code Was Interupted By User !!!")  # Inform of interruption
    exit(0)  # exit the program with status code 0 (success)


### End General Functions ###


### End Custom Functions ###

# %%####### Start Main Code ##########

### Initializations ###
atexit.register(cleanup)  # Tells the cleanup function to run at close
signal.signal(signal.SIGINT, handleInterrupt)  # Define the keyboardInterupt Response
startPrintTracking()  # Enable output tracking
print("\n")  # Break line
fancyPrint("Welcome to the RIT SPEX Rover")  # Welcome Message
# controller = wait4XboxController()                  # Loop to ensure X-Box controller connection
formSerialConnection()  # Connect to arduino
# [leftMotors, rightMotors] = initializeGPIO()        # Initialize GPIO motor objects


fancyPrint("Main Code has Begun")
### Main Code ###
presetInputProgram()  # A preset input program to test connections
# Main Loop
while True:
    # receiveXboxSignals(controller)  # xBox Based Controls
    manualInputs()  # Ask terminal for 5 commands

fancyPrint("The Program Has Completed")