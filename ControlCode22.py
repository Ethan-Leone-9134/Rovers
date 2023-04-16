# !/usr/bin/env python3
# -- coding: utf-8 -*-

# NOTE: Do not remove above code, it tells the pi what coding language is being used!

# Welcome, this is the RIT Spex Rover Pi control code. This is the code (as of 4/12/23) that controls the rover. 
# Depending on the active functions. The pi takes inputs from either a predetermined program or an xbox controller.
# It then sends those inputs to an arduino uno which does the actual control of the motors. 
# On termination, the pi sends instructions to the arduino to disable all motors then reset.
# The terminal is designed to give outputs for all connections, signals, and disconnections.

#%% Start Imports ###
import os                   # Additional python and pi interface
import sys                  # Used  track terminal output
import time                 # Allows to pause
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'       # Disable pygame welcome message
import pygame               # Interfaces with xbox controller
import atexit               # "At Exit" module for when code is terminated
import serial as ser        # Interfaces with the arduino
import RPi.GPIO as GPIO     # Used for controlling the motors from the pi
import math                 # Additional math functions
import signal               # Used to control keyboard interrupt
import threading
### End imports ###

#%% Start Formatting ###
pygame.init()                               # Initializes pygame
os.putenv('SDL_VIDEODRIVER', 'dummy')       # Disable digital display
### End Formatting ###

#%%####### Start Custom Functions ##########

# Directory ###
# Inputs    - Loops with pre-defined inputs
    # presetInputProgram    - Change speeds for motors from front to off to back to off
    # manualInputs          - Takes input from terminal
# xBox      - Functions that interface with the xBox controller
    # wait4XboxController   - Loop that runs until the xbox controller has been connected
    # receiveXboxSignals    - Process data sent from the xbox controller
    # calcDutyCycle         - Converts [-1, 1] range to duty cycle
    # buttonPressEvent      - Command for button presses
# GPIO      - Functions for pi control of motors
    # initGPIO        - Create the GPIO motor objects
    # setDuty               - Tells the arduino to set a motor to a duty cycle
# General   - Miscellaneous Functions
    # cleanUP               - Function that runs on termination of code
    # startPrintTracking    - Allows code to track all outputs to command window in a text file
    # fancyPrint            - Prints output in a formatted way with dashes for significant information
    # handleInterrupt       - Handles a Ctrl+C without displaying an error message

#%% Start Input Programs ###


def presetInputProgram():
    # Loop to Verify Outputs: Runs through each speed type for motors
    # Inputs  : none
    # Outputs : none
    # Globals : none

    while True:
        # 20% - Full Reverse    =       Rover Goes forwards
        # 30% - Stopped         =       Rover is not moving
        # 40% - Full Forward    =       Rover goes backwards

        dutyLeft = 30               # Initialize left duty cycle
        
        for i in [-1, 0, 1, 0]:     # Run loop for the values [-1,0,1,0]
            currMotor = 2            # Set duration of ramp cycle
            i = 0                   # Overwrite for a constant off duty cycle
            while currMotor > 0:
                dutyLeft = calcDutyCycle(i)         # Calculate duty cycle
                print("Python: Set the duty percentage to {}.".format(dutyLeft))    # Tell user what the pi is telling arduino
                setDuty(currMotor+3, 20)         # Set duty cycle
                currMotor = currMotor - 1
                time.sleep(2)
                print(" ")


def manualInputs():
    # Function takes an input of a pincode and a dutycycle from the terminal
    # Inputs  : none
    # Outputs : none
    # Globals : none

    pin = int(input("What pin code (1-6)? "))   # Get pin code
    duty = int(input("What duty cycle ? "))     # Get duty cycle
    setDuty(pin, duty)                          # Set value



#%% Start xBox Functinos

def wait4XboxController():
    # Function to delay program until x-box controller is connected
    # Inputs  : none
    # Outputs : none
    # Globals : none

    pygame.init()                                   # Initializes pygame
    pygame.joystick.init()                          # Initialize joystick data
    
    # Check if there are any joysticks already connected
    if pygame.joystick.get_count() > 0:                 # If a joystick has been connected
        controller = pygame.joystick.Joystick(0)        # Create controller variable
        controller.init()                               # Initialize controller
        fancyPrint("The {} is connected".format(controller.get_name()))
        return controller                               # Return variable
    
    # If no joysticks are connected, wait for one to be added
    while True:
        for event in pygame.event.get():            # Handle pygame events
            if event.type == pygame.JOYDEVICEADDED:   # If a joystick is connected
                controller = pygame.joystick.Joystick(0) # Create controller variable
                controller.init()                   # Initialize controller
                fancyPrint("The {} is connected".format(controller.get_name()))
                return controller                   # Return the initialized controller object
        print("Retrying controller connection...")   # Take a guess...
        time.sleep(2)                                # Two-second delay

def getController():
    controller = wait4XboxController()

    # print(pygame.version.ver)

    # # set the vibration to full power for 1 second
    # controller.set_vibration(1.0, 1.0)
    # time.sleep(0.5)
    # # stop the vibration
    # controller.set_vibration(0, 0)


    return controller


def receiveXboxSignals(cont):
    # Function to direct all data from the x-box controller
    # Inputs  : none
    # Outputs : none
    # Globals : none

    # Check for joystick events
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:   # Code for button press  # NOTE: MAPPING NEEDS VERIFICATION
            buttonPressEvent(event)

        if event.type == pygame.JOYAXISMOTION:  # Code for joystick motion
            if event.joy == 0:          # If left joystick
                if event.axis == 0:      # If x-axis
                    pass
                elif event.axis == 1:    # If y-axis
                    print(event.value)
                    dutyLeft = calcDutyCycle(event.value)
                    for i in range(3):
                        i = i+1
                        setDuty(i, round(dutyLeft))
                        print("Pin {} to {}".format(i,dutyLeft))

                                        # If right joystick
                elif event.axis == 2:      # If x-axis
                    pass
                elif event.axis == 3:    # If y-axis
                    dutyRight = calcDutyCycle(-(event.value))
                    for i in range(3):
                        i = i+4
                        setDuty(i, round(dutyRight))
        time.sleep(0.001)


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

    offset = 30 - 4.5                                # Neutral dutyCycle
    if (signal >= -0.01) and (signal <= 0.09):      # If joysticks are likely untouched
        duty = offset                                # Prevent motion
    else:                                           # If signal seems intentional
        duty = -10 * signal + offset            # Run Conversion algorithm for joystick to dutyCycle
    return duty


def buttonPressEvent(event):
    # Function for whenever an xbox button is pressed
    # Inputs  : event - event of button press
    # Outputs : none
    # Globals : none

    if event.button == 11:   # Middle Right "Menu" Button
        fancyPrint("Menu Button Pressed")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 0:  # "A" Button
        print("button 0 down")
    elif event.button == 1:  # "B" Button
        print("button 1 down")
    elif event.button == 2:  # 
        print("button 2 down")
    elif event.button == 3:     # "X" Button
        print("button 3 down")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 4:     # "Y" Button
        # setDuty(4, 20)
        # setDuty(5, 40)
        # time.sleep(6)
        # setDuty(4, 30)
        # setDuty(5, 30)
        print("button 4 down")
    elif event.button == 5:  
        print("button 5 down")
    elif event.button == 6:     # Left Bumper
        print("button 6 down")
    elif event.button == 7:     # Right Bumper
        print("button 7 down")
    elif event.button == 8:     # Left joystick button
        print("button 8 down")
    elif event.button == 9:     # Right joystick button
        print("button 9 down")
    elif event.button == 10:    # XBOX button
        print("button 10 down")


### End xBox Functions

#%% Start GPIO Functions ###

def initGPIO():
    class GPIOPin:
        ## NOTE: From ChatGPT
        def __init__(self, pin_num):
            self.pin_num = pin_num
            self.frequency = 200
            self.duty_cycle = 0
            GPIO.setup(self.pin_num, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pin_num, self.frequency)
            self.pwm.start(self.duty_cycle)
            self.lock = threading.Lock()
        
        def setDutyCycle(self, new_duty):
            with self.lock:
                self.duty_cycle = new_duty
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                
        def stop(self):
            self.pwm.stop()
            GPIO.cleanup(self.pin_num)

    GPIO.setwarnings(False)     # Disable GPIO warnings
    GPIO.setmode(GPIO.BCM)      # Change GPIO Mode
    p1 = GPIOPin(1)
    p2 = GPIOPin(16)
    p3 = GPIOPin(20)
    p4 = GPIOPin(0)
    p5 = GPIOPin(5)
    p6 = GPIOPin(6)

    return [p1, p2, p3, p4, p5, p6]


def setDuty(motorCode, dutyCycle):
    # Change a motor's duty cycle
    # Inputs  : motorCode - number of motor to be change [(1-3) - Left]   [(4-6) - Right]
    #           dutyCycle - target duty cycle to set motor to
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino
    # Example : setDuty(1, 20) - Sets Front Left motor to 20

    global motorPins
    motorPins[motorCode-1].setDutyCycle(dutyCycle)


#%% Start General Functions ###


def cleanUP():
    # Callback function to disable the motors attached to the arduino
    # Inputs  : none
    # Outputs : none
    # Globals : uno     -   Calls the arduino communication variable
    GPIO.cleanup()

    fancyPrint("Program Terminated")        # Inform of termination


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

    dashLen = 50                                                    # Number of dashes
    breakLine = "-" * dashLen                                       # Create the breakline
    with open("/home/spex/Desktop/outputLogs.txt", 'r') as f:       # Open the log file
        lines = f.readlines()                                           # Read the last line
        if "-------" not in lines[-1].strip():                          # If there was no breakline above
            print(breakLine)                                                # Add a breakline
        textLength = len(inputText)                                     # Length of input
        sides = math.floor((dashLen - textLength - 2) / 2)              # Finds amount of side dashes
        sides = '-' * sides                                             # Generates side walls
        if textLength % 2 == 0:                                         # If text length is even
            print(sides + " " + inputText + " " + sides)                    # Normal formatted print
        else:                                                           # If text length is odd
            print(sides + " " + inputText + " -" + sides)                   # Formatted print with an extra dash
        print(breakLine)                                                # Print ending breakline


def handleInterrupt(signum, frame):
    # Modifies the keyboardInterupt Event
    # Inputs  : none
    # Outputs : none
    # Globals : none

    print('\n')                                             # Better looks
    fancyPrint("!!! Code Was Interupted By User !!!")       # Inform of interruption
    exit(0)                                                 # exit the program with status code 0 (success)


### End General Functions ###


### End Custom Functions ###

#%%####### Start Main Code ##########

### Initializations ###
atexit.register(cleanUP)                            # Tells the cleanup function to run at close
signal.signal(signal.SIGINT, handleInterrupt)       # Define the keyboardInterupt Response
startPrintTracking()                                # Enable output tracking
print("\n")                                         # Break line
fancyPrint("Welcome to the RIT SPEX Rover")         # Welcome Message
# controller = wait4XboxController()                  # Loop to ensure X-Box controller connection
controller = getController()
global motorPins
# [m1,m2,m3,m4,m5,m6] = initializeGPIO()        # Initialize GPIO motor objects
# [m1,m2,m3,m4,m5,m6] = initGPIO()
motorPins = initGPIO()

fancyPrint("Main Code has Begun")
print("What duty cycle? 30")
### Main Code ###

# presetInputProgram()            # A preset input program to test connections
# Main Loop
while True:
    receiveXboxSignals(controller)  # xBox Based Controls
    # value = int(input("What duty cycle? "))
    # baseline = value-4
    # for i in range(6):
    #     i = i+1
    
    #     setDuty(i, baseline)


fancyPrint("The Program Has Completed")

