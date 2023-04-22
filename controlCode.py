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
import time                 # Allows to pause
import atexit               # "At Exit" module for when code is terminated
import signal               # Used to control keyboard interrupt
import threading            # Imporves GPIO settings
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'       # Disable pygame welcome message
import pygame               # Interfaces with xbox controller
import RPi.GPIO as GPIO     # Used for controlling the motors from the pi

import fancy
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
        fancy.Print("The {} is connected".format(controller.get_name()))
        return controller                               # Return variable
    
    # If no joysticks are connected, wait for one to be added
    while True:
        for event in pygame.event.get():            # Handle pygame events
            if event.type == pygame.JOYDEVICEADDED:   # If a joystick is connected
                controller = pygame.joystick.Joystick(0) # Create controller variable
                controller.init()                   # Initialize controller
                fancy.Print("The {} is connected".format(controller.get_name()))
                return controller                   # Return the initialized controller object
        print("Retrying controller connection...")   # Take a guess...
        time.sleep(2)                                # Two-second delay


def getController():

    controller = wait4XboxController()

    # Set up the event queue
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.QUIT])

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

    global contMode

    # Check for joystick events
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:   # Code for button press  # NOTE: MAPPING NEEDS VERIFICATION
            buttonPressEvent(event)
        if event.type == pygame.JOYAXISMOTION:  # Code for joystick motion
            if contMode:        # SOLO MODE
                soloControls(event, cont)
            else:               # DUO MODE
                duoControls(event)
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

    offset = 30 - 2                                 # Neutral dutyCycle
    if (signal >= -0.01) and (signal <= 0.09):      # If joysticks are likely untouched
        duty = offset                                # Prevent motion
    else:                                           # If signal seems intentional
        duty = -10 * signal + offset            # Run Conversion algorithm for joystick to dutyCycle
    return duty


def buttonPressEvent(event):
    # Function for whenever an xbox button is pressed
    # Inputs  : event - event of button press
    # Outputs : none
    # Globals : contMode - Mode for controls, either solo (1) or duo (0)

    global contMode

    if event.button == 11:   # Middle Right "Menu" Button
        # fancy.Print("Menu Button Pressed")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 0:  # "A" Button
        setColor("green")
        print("button 0 down")
    elif event.button == 1:  # "B" Button
        print("button 1 down")
    elif event.button == 2:  # 
        print("button 2 down")
    elif event.button == 3:     # "X" Button
        # print("button 3 down")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 4:     # "Y" Button
        setColor("yellow")
        print("button 4 down")
    elif event.button == 5:  
        print("button 5 down")
    elif event.button == 6:     # Left Bumper
        contMode = 1
        fancy.Print("Button Mode Set to Solo")
        setColor("magenta")
        time.sleep(0.5)
        setColor("orange")
        # print("button 6 down")
    elif event.button == 7:     # Right Bumper
        contMode = 0
        setColor("cyan")
        time.sleep(0.5)
        setColor("orange")
        fancy.Print("Button Mode Set to Duo")
        # print("button 7 down")
    elif event.button == 8:     # Left joystick button
        print("button 8 down")
    elif event.button == 9:     # Right joystick button
        print("button 9 down")
    elif event.button == 10:    # XBOX button
        print("button 10 down")


def soloControls(event, cont):

    
    Xval = cont.get_axis(0)                     # Get the current values of the x-axis and y-axis
    Yval = cont.get_axis(1)
    maxRad = math.sqrt(Xval ** 2 + Yval ** 2)   # Calculate the magnitude of the vector
    theta = math.atan2(Yval, Xval)              # Calculate the angle in radians
    speedLeft = maxRad * math.sin(theta + math.pi/4)
    speedRght = maxRad * math.cos(theta + math.pi/4)

    if Xval < 0:
        speedLeft *= abs(Xval)
    else:
        speedRght *= abs(Xval)
    
    if Yval < 0:
        speedLeft *= abs(Yval)
    else:
        speedRght *= abs(Yval)

    dutyLeft = calcDutyCycle(speedLeft)
    for i in range(3):
        i = i+1
        setDuty(i, round(dutyLeft))

    
    dutyRight = calcDutyCycle(speedRght)
    for i in range(3):
        i = i+4
        setDuty(i, round(dutyRight))
    


def duoControls(event):
    # If left joystick
    if event.axis == 0:      # If x-axis
        pass
    elif event.axis == 1:    # If y-axis
        dutyLeft = calcDutyCycle(event.value)
        for i in range(3):
            i = i+1
            setDuty(i, round(dutyLeft))
    # If right joystick
    elif event.axis == 2:      # If x-axis
        pass
    elif event.axis == 3:    # If y-axis
        dutyRight = calcDutyCycle(-(event.value))
        for i in range(3):
            i = i+4
            setDuty(i, round(dutyRight))


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

    r = GPIOPin(2)
    g = GPIOPin(3)
    b = GPIOPin(4)
    global rgb
    rgb = [r, g, b]

    p1 = GPIOPin(1)     # Front Left
    p2 = GPIOPin(16)    # Middle Left
    p3 = GPIOPin(20)    # Back Left
    p4 = GPIOPin(0)     # Front Right
    p5 = GPIOPin(5)     # Middle Right
    p6 = GPIOPin(6)     # Back Right

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


def setColor(r, g=None, b=None):
    # Sets the colors of the RGB LED strip
    # Inputs  : r,g,b - red,green,blue values from 0-255
    # Outputs : none
    # Globals : rgb - contains the GPIO pins
    # Note: If only one argument is given, it will be interpreted as a pre-coded color

    global rgb

    # Predefined color values from ChatGPT
    colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'off': (0, 0, 0),
        'yellow': (255, 255, 0),
        'magenta': (255, 0, 255),
        'cyan': (0, 255, 255),
        'orange': (255, 128, 0),
        'pink': (255, 192, 203),
        'purple': (128, 0, 128),
        'lavender': (230, 230, 250),
        'turquoise': (64, 224, 208),
        'gold': (255, 215, 0),
        'silver': (192, 192, 192)
    }

    # Check if only one argument is given
    if g is None and b is None:
        # Interpret as a pre-coded color
        if r in colors:
            r, g, b = colors[r]
        else:
            raise ValueError("Invalid pre-coded color")
    
    rgb[0].setDutyCycle(r/2.55)
    rgb[1].setDutyCycle(g/2.55)
    rgb[2].setDutyCycle(b/2.55)




#%% Start General Functions ###



def cleanUP():
    # Callback function to disable the motors attached to the arduino
    # Inputs  : none
    # Outputs : none
    # Globals : uno     -   Calls the arduino communication variable

    GPIO.cleanup()                      # Disable gpio pins
    # arduino.exit()                      # Disconnect Arduino
    fancy.Print("Program Terminated")   # Inform of termination
    fancy.close()                       # Delete fancy text file


def handleInterrupt(signum, frame):
    # Modifies the keyboardInterupt Event
    # Inputs  : none
    # Outputs : none
    # Globals : none

    print('\n')                                             # Better looks
    fancy.Print("!!! Code Was Interupted By User !!!")       # Inform of interruption
    exit(0)                                                 # exit the program with status code 0 (success)


### End General Functions ###


### End Custom Functions ###

#%%####### Start Main Code ##########

### Initializations ###
atexit.register(cleanUP)                            # Tells the cleanup function to run at close
signal.signal(signal.SIGINT, handleInterrupt)       # Define the keyboardInterupt Response
fancy.start()                                       # Enable output tracking
# arduino.connect()                                   # Connect to the arduino
print("\n")                                         # Break line
fancy.Print("Welcome to the RIT SPEX Rover")        # Welcome Message



global motorPins, contMode
motorPins = initGPIO()                  # Activate GPIO Pins
contMode = 0
setColor("red")

controller = getController()            # Connect to X-Box Controller
fancy.Print("Main Code has Begun")
setColor("green")


### Main Loop ###
while True:
    receiveXboxSignals(controller)  # xBox Based Controls


fancy.Print("The Program Has Completed")
