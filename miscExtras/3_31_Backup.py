# !/usr/bin/env python3
# -- coding: utf-8 -*-

# NOTE: Do not remove above code, it tells the pi what coding language is being used!

# Welcome, this is the RIT Spex Rover Pi control code. This is the code (as of 3/31/23) that controls the rover.
# Depending on the active functions. The pi takes inputs from either a predetermined program or an xbox controller.
# It then sends those inputs to an arduino uno which does the actual control of the motors.
# On termination, the pi sends instructions to the arduino to disable all motors then reset.
# The terminal is designed to give outputs for all connections, signals, and disconnections.

# %% Start Imports ###
import os  # Basic python import
import time  # Allows to pause
import pygame  # Interfaces with xbox controller
import atexit  # "At Exit" module for when code is terminated
import serial as ser  # Interfaces with the arduino

### End imports ###

# %% Start Formatting ###
pygame.init()  # Initializes pygame
print("\n-----------------------------------------")
print("----- Welcome to the RIT SPEX Rover -----")
print("-----------------------------------------")
os.putenv('SDL_VIDEODRIVER', 'dummy')  # Disable digital display


### End Formatting ###

# %%####### Start Custom Functions ##########


# %% Start Arduino Function ###


def formSerialConnection():
    # Function to establish a connection with the arduino
    # Inputs  - none
    # Outputs - none

    global uno  # Serial communication variable
    validity = 1
    while validity:
        try:
            # uno = ser.Serial('/dev/ttyACM0', 115200, timeout=.1)     # Enable arduino communication (pi)
            uno = ser.Serial('/dev/ttyACM0', 115200, timeout=0.1)  # Enable arduino communication (pi)
            # uno = ser.Serial('COM5', 115200, timeout=.1)              # Enable arduino communication (laptop)
        except:
            print("ERROR : Arudino not connected to Pi")
            time.sleep(0.5)
        else:
            time.sleep(1.8)
            print("--- Arduino Connection Is Established ---")
            print("-----------------------------------------")
            #     time.sleep(0.1)
            validity = 0


def resetArduino():
    global uno
    uno.setDTR(False)  # Set active to false
    time.sleep(0.1)  # Give it 1/10 second to process
    uno.setDTR(True)  # Set active to true
    time.sleep(2)  # Allow uno to setup and start


def setDuty(motorCode, dutyCycle):
    # Tells the arduino to change a motor's duty cycle
    # Inputs  : motorCode - number of motor to be change [(1-3) - Left]   [(4-6) - Right]
    #           dutyCycle - target duty cycle to set motor to
    # Outputs : none
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
    # Loop to Verify Outputs: Runs through each speed type for "currTime" motors
    # Inputs  : none
    # Outputs : none

    while True:
        # 20% - Full Reverse    =       Rover Goes forwards
        # 30% - Stopped         =       Rover is not moving
        # 40% - Full Forward    =       Rover goes backwards

        dutyLeft = 30  # Initialize left duty cycle

        for i in [-1, 0, 1, 0]:  # Run loop for the values [-1,0,1,0]
            currTime = 2  # Set duration of ramp cycle
            i = 0
            while currTime > 0:
                startTime = time.time()
                dutyLeft = calcDutyCycle(i)  # Calculate duty cycle
                print("Python: Set the duty percentage to {}.".format(
                    dutyLeft))  # Tell user what the pi is telling arduino
                setDuty(currTime + 3, 20)  # Set duty cycle
                # print("The current i value is {i}. The current duty percent is {dutyLeft}. Remaining time is {currTime}")
                # print(time.time()-startTime)
                currTime = currTime - 1
                time.sleep(2)
                print(" ")


def dramaticInputProgram():
    # Loop to Verify Outputs with emphasis on displays
    # Inputs  : none
    # Outputs : none

    dutyLeft = 36  # Basic dutyCycle variable
    while True:
        if dutyLeft > 40:  # If past usable range
            dutyLeft = 30  # Drop to off
        else:  # Otherwise
            dutyLeft = dutyLeft + 2  # Increment duty cycle

        for i in range(3):
            print(" ")
            time.sleep(1)
            print(3)
            time.sleep(1)
            print(2)
            time.sleep(1)
            print(1)
            time.sleep(1)
            startTime = time.time()
            print("Python: Set the duty percentage to {}.".format(dutyLeft))
            setDuty(i + 1, dutyLeft)
            print("Done in {} seconds".format(round(time.time() - startTime, 5)))


# %% Start xBox Functinos

def wait4XboxController():
    # Function to delay program until x-box controller is connected
    # Inputs  - none
    # Outputs - none
    pygame.init()  # Initializes pygame
    pygame.joystick.init()  # Initialize joystick data

    # Check if there are any joysticks already connected
    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print("!!! The {} is already connected !!!".format(controller.get_name()))
        return controller

    # If no joysticks are connected, wait for one to be added
    while True:
        for event in pygame.event.get():  # Handle pygame events
            if event.type == pygame.JOYDEVICEADDED:  # If a joystick is connected
                controller = pygame.joystick.Joystick(0)  # Create controller variable
                controller.init()  # Initialize controller
                print("!!! The {} is connected !!!".format(controller.get_name()))
                return controller  # Return the initialized controller object
        print("Retrying controller connection...")  # Take a guess...
        time.sleep(2)  # Two-second delay


def wait6XboxController():
    # Function to delay program until x-box controller is connected
    # Inputs  - none
    # Outputs - none
    pygame.init()  # Initializes pygame
    pygame.joystick.init()  # Initialize joystick data
    while True:
        for event in pygame.event.get():  # Handle pygame events
            if event.type == pygame.JOYDEVICEADDED:  # If a joystick is connected
                controller = pygame.joystick.Joystick(0)  # Create controller variable
                controller.init()  # Initialize controller
                print("!!! The {} is connected !!!".format(controller.get_name()))
                return controller  # Return the initialized controller object
        print("Retrying controller connection...")  # Take a guess...
        time.sleep(2)  # Two-second delay


def mainXboxControlledLoop(cont):
    while True or KeyboardInterrupt:
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

# %% Start General Functions ###


def cleanup():
    # Callback function to disable the motors attached to the arduino
    # Inputs  - none
    # Outputs - none

    global uno  # Calls the arduino communication variable
    for pin in [1, 4, 2, 5, 3, 6]:  # Repeat for each pin from front to back
        setDuty(pin, 30)  # Disable motor
    print("----------------------------")  # Ending display
    try:
        time.sleep(0.5)  # Let arduino disable motors
        resetArduino()  # Restart arduino
        uno.close()  # End arduino communication
    except:
        pass
    else:
        print("--- Arduino Disconnected ---")
        print("----------------------------")
    print("---- Program Terminated ----")
    print("----------------------------")


def manualInputs():
    for i in range(5):
        pin = input("What pin code (1/4)?")
        duty = input("What duty cycle ?")
        setDuty(pin, duty)


### End General Functions ###


### End Custom Functions

# %%####### Start Main Code ##########

# Initializations
offset = 30  # No motion duty cycle
cycle = 30  # Duty cycle info
freq = 200  # Duty cycle frequency
atexit.register(cleanup)  # Tells the cleanup function to run at close

# Esatablish connections
controller = wait4XboxController()  # Loop to ensure X-Box controller connection
formSerialConnection()  # Connect to arduino

print("On input Programs")
# Input programs
# presetInputProgram()            # A preset input program to test connections
# manualInputs()                  # Ask terminal for 5 commands
mainXboxControlledLoop(controller)  # xBox Based Controls

print("--- The program has been completed ---")