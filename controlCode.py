#!/usr/bin/env python3
# -- coding: utf-8 -*-

# NOTE: Do not remove above code, it tells the pi what coding language is being used!

"""
Welcome, this is the RIT Spex Rover Pi control code. This is the code (as of 4/29/23) that controls the rover. 
The raspberry pi takes inputs from an xbox controller. GPIO pins are used for control.
The left joystick controls the left wheels, the right joystick controls the right wheels.
Pressing bumpers changes which way is considered the "front" of the rover.
The terminal is designed to give outputs for all connections, signals, and disconnections.
"""

#%% Start Imports ###
import os                   # Additional python and pi interface
import time                 # Allows to pause
import atexit               # "At Exit" module for when code is terminated
import signal               # Used to control keyboard interrupt
import threading            # Imporves GPIO settings
import math                 # Used for math stuffs

if os.environ.get('TERM') != 'xterm-256color':      # Checks that code is run at startup
    time.sleep(10)                                  # Add a pause for everything to catchup
 
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'       # Disable pygame welcome message
import pygame               # Interfaces with xbox controller
import RPi.GPIO as GPIO     # Used for controlling the motors from the pi

import fancy                # Custom Module used for formatted printing
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
    # getController         - Used to output the xbox controller to the rest of the script
    # receiveXboxSignals    - Process data sent from the xbox controller
    # calcDutyCycle         - Converts [-1, 1] range to duty cycle
    # buttonPressEvent      - Command for button presses
    # duoControlsFront      - Primary controls for forward motion
    # duoControlsBack       - Secondary controls for backwarsds motion
# GPIO      - Functions for pi control of motors
    # initGPIO        - Create the GPIO motor objects
    # setDuty               - Tells the arduino to set a motor to a duty cycle
# General   - Miscellaneous Functions
    # cleanUP               - Function that runs on termination of code
    # handleInterrupt       - Handles a Ctrl+C without displaying an error message

# Globals : rgb         - Controls LED pins
#           inReverse   - Boolean for the controls being inverted
#           aPresses    - Tracks timestamps of "A" button presses
#           slowMode    - Boolean for half speed mode

global rgb, inReverse, aPresses, slowMode

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



#%% Start xBox Functions

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
    # Functions handles activation of the xbox controller and changes LEDs
    # Inputs  : None
    # Outputs : controller - xBox controller variable
    # Globals : rgb         - Controls LED pins
    #           inReverse   - Boolean for the controls being inverted
    #           aPresses    - Tracks timestamps of "A" button presses
    #           slowMode    - Boolean for half speed mode

    global rgb, inReverse, aPresses, slowMode

    inReverse = 0                           # Disable reverse mode
    aPresses = []                           # Tracks a Presses
    slowMode = 0                            # Sets speed to full
    rgb.setColor("red")                     # Set LEDs to red
    time.sleep(1)                           # Delay to highlight red light
    controller = wait4XboxController()      # Waits until controller is connected
    pygame.event.set_blocked(None)          # Set up the event queue
    pygame.event.set_allowed([pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.QUIT])

    # print(pygame.version.ver)
    # # set the vibration to full power for 1 second
    # controller.set_vibration(1.0, 1.0)
    # time.sleep(0.5)
    # # stop the vibration
    # controller.set_vibration(0, 0)

    rgb.setColor("green")                   # Set LEDs to green
    return controller


def receiveXboxSignals(cont):
    # Function to direct all data from the x-box controller
    # Inputs  : none
    # Outputs : none
    # Globals : inReverse - Boolean variable for the controls being inverted

    global inReverse

    # Check for joystick events
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:   # Code for button press  # NOTE: MAPPING NEEDS VERIFICATION
            buttonPressEvent(event)
        if event.type == pygame.JOYAXISMOTION:  # Code for joystick motion
            if inReverse:        # Invert Controls
                duoControlsBack(event)
            else:                # Normal Controls
                duoControlsFront(event)
        time.sleep(0.001)


def calcDutyCycle(signal):
    # Function to set the new value of the duty cycle from xbox controller
    # Inputs  : signal   - xbox joystick value (event.value)
    # Outputs : duty     - value of updated duty cycle
    # Globals : slowMode - Boolean for half speed mode
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

    global slowMode

    offset = 30 - 1                                # Neutral dutyCycle
    if (signal >= -0.01) and (signal <= 0.09):      # If joysticks are likely untouched
        duty = offset                                # Prevent motion
    else:                                           # If signal seems intentional
        duty = (-10+3*slowMode) * signal + offset    # Run Conversion algorithm for joystick to dutyCycle
    return duty


def buttonPressEvent(event):
    # Function for whenever an xbox button is pressed
    # Inputs  : event - event of button press
    # Outputs : none
    # Globals : rgb         - Controls LED pins
    #           inReverse   - Boolean for the controls being inverted
    #           aPresses    - Tracks timestamps of "A" button presses
    #           slowMode    - Boolean for half speed mode

    global rgb, inReverse, aPresses, slowMode

    if event.button == 11:   # Middle Right "Menu" Button
        # fancy.Print("Menu Button Pressed")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 0:  # "A" Button
        currentTime = time.time()               # Record time
        aPresses.append(currentTime)            # Add the press to the holder variable
        print(aPresses)
        if len(aPresses) >= 3:                   # If there have been least 3 clicks
            print(currentTime - aPresses[-2])
            if currentTime - aPresses[-2] < 1:      # If the last three clicks all happened within one second
                slowMode = not(slowMode)                # Swap slowmode
                if slowMode:                       # Tells user about any changes
                    fancy.Print("Slow Mode Activated")
                    rgb.setGreen(80)
                else:
                    fancy.Print("Normal Speed Activated")
                    rgb.setGreen(255)
                aPresses = []                           # Clear a presses
        if len(aPresses) > 3:                 # Clear trailing timestamps
                aPresses = aPresses[-2:]
        print("button 0 down")
    elif event.button == 1:  # "B" Button
        print("button 1 down")
    elif event.button == 2:  # 
        print("button 2 down")
    elif event.button == 3:     # "X" Button
        # print("button 3 down")
        handleInterrupt(signal.SIGINT, None)     # Instantly kill script
    elif event.button == 4:     # "Y" Button
        print("button 4 down")
    elif event.button == 5:  
        print("button 5 down")
    elif event.button == 6:     # Left Bumper
        inReverse = 1               # Set boolean to true
        rgb.setBlue(255)            # Activate Reverse Indicator
        fancy.Print("Rover is Now in Reverse")
        # print("button 6 down")
    elif event.button == 7:     # Right Bumper
        inReverse = 0               # Set boolean to false
        rgb.setBlue(0)              # Activate Reverse Indicator
        fancy.Print("Rover is Now Front Facing")
        # print("button 7 down")
    elif event.button == 8:     # Left joystick button
        print("button 8 down")
    elif event.button == 9:     # Right joystick button
        print("button 9 down")
    elif event.button == 10:    # XBOX button
        print("button 10 down")
   

def duoControlsFront(event):
    # Function for primary front facing controls
    # Inputs  : event - event for the axis change
    # Outputs : none
    # Globals : none

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


def duoControlsBack(event):
    # Function for secondary backwards facing controls
    # Inputs  : event - event for the axis change
    # Outputs : none
    # Globals : none

    # If left joystick
    if event.axis == 0:      # If x-axis
        pass
    elif event.axis == 1:    # If y-axis
        dutyLeft = calcDutyCycle((event.value))
        for i in range(3):
            i = i+4
            setDuty(i, round(dutyLeft))
    # If right joystick
    elif event.axis == 2:      # If x-axis
        pass
    elif event.axis == 3:    # If y-axis
        dutyRight = calcDutyCycle(-(event.value))
        for i in range(3):
            i = i+1
            setDuty(i, round(dutyRight))


### End xBox Functions

#%% Start GPIO Functions ###

def initGPIO():
    # Functions initializes all GPIO pins for motors and LEDs
    # Inputs  : none
    # Outputs : Motor Pins
    # Globals : rgb - Controls LED pins

    class GPIOPin:
        ## NOTE: From ChatGPT
        def __init__(self, pin_num, freq):        # Creates the pin variable
            self.pin_num = pin_num              # Pin number
            self.frequency = freq                # PWM Frequency
            self.duty_cycle = 0                 # Start duty cycle at zero
            GPIO.setup(self.pin_num, GPIO.OUT)  # Set as an output pin
            self.pwm = GPIO.PWM(self.pin_num, self.frequency)   # Declare signal type
            self.pwm.start(self.duty_cycle)     # Start the pwm signal
            self.lock = threading.Lock()        # Manipulate the thread
        
        def setDutyCycle(self, new_duty):   # Properly changes duty cycle
            with self.lock:                     # Allows for safe setting of the duty cycle
                self.duty_cycle = new_duty          # Overwrite storage value
                self.pwm.ChangeDutyCycle(self.duty_cycle)   # Actually change the pwm signal
                
        def stop(self):                     # Used to delete the pin data
            self.pwm.stop()                     # Directly stops
            GPIO.cleanup(self.pin_num)          # Cleans up the pins values

    # class motorPins:
    #     def __init__(self, pinNumbers):
    #         for i in pinNumbers:


    class RGBPins:
        def __init__(self, pin1, pin2, pin3):
            self.redPin = GPIOPin(pin1, 1000)
            self.greenPin = GPIOPin(pin2, 1000)
            self.bluePin = GPIOPin(pin3, 1000)
        def setRed(self, value):
            self.redPin.setDutyCycle(value/2.55)
        def setGreen(self, value):
            self.greenPin.setDutyCycle(value/2.55)
        def setBlue(self, value):
            self.bluePin.setDutyCycle(value/2.55)
        def setColor(self, name):
            colorTrip = get_color(name)
            self.redPin.setDutyCycle(colorTrip[0]/2.55)
            self.greenPin.setDutyCycle(colorTrip[1]/2.55)
            self.bluePin.setDutyCycle(colorTrip[2]/2.55)
           
    GPIO.setwarnings(False)     # Disable GPIO warnings
    GPIO.setmode(GPIO.BCM)      # Change GPIO Mode

    global rgb
    rgb = RGBPins(2, 3, 4)

    p1 = GPIOPin(1, 200)
    p1.setDutyCycle(28)
    p2 = GPIOPin(16, 200)
    p2.setDutyCycle(28)
    p3 = GPIOPin(20, 200)
    p3.setDutyCycle(28)
    p4 = GPIOPin(0, 200)
    p4.setDutyCycle(28)
    p5 = GPIOPin(5, 200)
    p5.setDutyCycle(28)
    p6 = GPIOPin(6, 200)
    p6.setDutyCycle(28)

    return [p1, p2, p3, p4, p5, p6]


def get_color(name):
    # Function converts a name to an RGB triple
    # Inputs  : name - Name of the color
    # Outputs : Triple of rgb values
    # Globals : none

    switcher = {
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
    return switcher.get(name, [0, 0, 0])


def setDuty(motorCode, dutyCycle):
    # Change a motor's duty cycle
    # Inputs  : motorCode - number of motor to be change [(1-3) - Left]   [(4-6) - Right]
    #           dutyCycle - target duty cycle to set motor to
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino
    # Example : setDuty(1, 20) - Sets Front Left motor to 20

    global motorPins 
    curr = motorPins[motorCode-1].duty_cycle
    tempNew = dutyCycle
    stepValue = 100
    if abs((tempNew) - (curr)) >= stepValue:    # If the distance between the current and desired is > 1
        if tempNew > curr:                          # If the value of the desired duty is greater than the current value
            new = curr + stepValue                      # Set output to current value + 1
        else:                                       # If the value of the desired is less than the current value
            new = curr - stepValue                      # Set output to current value - 1
    else:                                       # If the value is does not exceed the step
        new = tempNew                               # Set output to tempNew

    motorPins[motorCode-1].setDutyCycle(new)




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
print("\n")                                         # Break line
fancy.Print("Welcome to the RIT SPEX Rover")        # Welcome Message


motorPins = initGPIO()                  # Activate GPIO Pins


controller = getController()            # Connect to X-Box Controller
fancy.Print("Main Code has Begun")


### Main Loop ###
while True:
    receiveXboxSignals(controller)          # xBox Based Controls
    if pygame.joystick.get_count() == 0:    # Detect disconnection
        for i in range(6):                      # For each motor
            setDuty(i+1, 30)                        # Disable motor
        controller = getController()            # Attempt reconnection (DOES NOT WORK)


fancy.Print("The Program Has Completed")
