# !/usr/bin/env python3
# -- coding: utf-8 -*-


### Start Imports
# We use Pygame to access the Xbox One Controller
import RPi.GPIO as GPIO
import os
import time
import pygame
from pygame.constants import JOYBUTTONDOWN


### Start Custom Functions
def rampMotor(curr, target):
    # Converts -1<x<1 xbox signal to a ramped value for the pwm control
    # Inputs    : curr - current pwm value for the desired motor
    #           : target - -1<x<1 xbox signal to get modified
    # Outputs   : new - ramped signal

    offset = 30
    if (target >= -0.01) and (target <= 0.09):
        tempNew = offset  # Prevents motion when inputs appear to be untouched
    else:
        tempNew = -10 * target + offset  # Implements equation to find proper percentages from xbox inputs
        # print("Step-In: curr = {}".format(curr))
        # print("Step-In: tempNew = {}".format(tempNew))

    # tempNew - Dummy variable for converted Target value

    # Right now the signal has been converted to a percentage
    # It will now get ramped
    stepValue = 1
    if abs((tempNew) - (curr)) >= stepValue:  # If the distance between the current and desired is > 1
        if tempNew > curr:  # If the value of the desired duty is greater than the current value
            new = curr + stepValue  # Set output to current value + 1
        else:  # If the value of the desired is less than the current value
            new = curr - stepValue  # Set output to current value - 1
    else:  # If the value is does not exceed the step
        new = tempNew  # Set output to tempNew

    return new  # Send the output


def wait4XboxController():
    # Loop to ensure X-Box controller connection
    # Function has no inputs and no outputs
    while True:  # Loop runs until a connection is found
        try:  # Code will attempt to run this section
            joysticks = []  # Initialize joysticks
            pygame.init()
            for i in range(0, pygame.joystick.get_count()):
                joysticks.append(pygame.joystick.Joystick(i))
                joysticks[-1].init()
            # Print out the name of the controller
            print("!!! The {} is connected !!!".format(pygame.joystick.Joystick(0).get_name()))
        except Exception as e:  # Run when code errors (the controller is not connected)
            print("Retrying controller connection...")
            print(e)
            time.sleep(2)
        else:
            print("!!! The {} is connected !!!".format(pygame.joystick.Joystick(0).get_name()))
            break  # End loop if there is no error

    print("!!! The controller is connected !!!")


### Start Main Code
os.putenv('SDL_VIDEODRIVER', 'dummy')
offset = 30
cycle = 30
freq = 200;
GPIO.cleanup()

# Loop to ensure X-Box controller connection
# wait4XboxController()


### Initializes Pinmodes for the pi controls
leftMotorPin0 = 12  # Set left motor pins
# leftMotorPin1 = 10
# leftMotorPin2 = 12
rightMotorPin0 = 13  # Set right motor pins
# rightMotorPin1 = 38
# rightMotorPin2 = 40
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(leftMotorPin0, GPIO.OUT)  # GPIO Setups fo left motor
# GPIO.setup(leftMotorPin1,GPIO.OUT)
# GPIO.setup(leftMotorPin2,GPIO.OUT)
GPIO.setup(rightMotorPin0, GPIO.OUT)  # GPIO Setups for right motor
# GPIO.setup(rightMotorPin1,GPIO.OUT)
# GPIO.setup(rightMotorPin2,GPIO.OUT)
leftMotor0 = GPIO.PWM(leftMotorPin0, freq)  # Activate PWM Signals for left motor
leftMotor0.start(0)
# leftMotor1 = GPIO.PWM(leftMotorPin1,freq)
# leftMotor1.start(0)
# leftMotor2 = GPIO.PWM(leftMotorPin2,freq)
# leftMotor2.start(0)

rightMotor0 = GPIO.PWM(rightMotorPin0, freq)  # Activate PWM Signals for right motors
rightMotor0.start(0)
# rightMotor1 = GPIO.PWM(rightMotorPin1,freq)
# rightMotor1.start(0)
# rightMotor2 = GPIO.PWM(rightMotorPin2,freq)
# rightMotor2.start(0)


# Xbox Joystick Axis:
# Axis 0 - Up/Down      -   Down value is -1    Up value is 1
# Axis 1 - Left/Right   -   Left value is -1    Right value is 1
# Center is always 0
#

min_val = float('inf')
max_val = -float('inf')

### Main Loop ###

# Loop to Verify Outputs
while True:
    # offset = 30   &   cycle = 30
    # 20% - Full Reverse    =       Rover Goes forwards
    # 30% - Stopped         =       Rover is not moving
    # 40% - Full Forward    =       Rover goes backwards
    dutyLeft = 40;
    for i in [-1, -1, -1, -1]:  # Run loop for the values [-1,0,1,0]
        currTime = 40;
        while currTime >= 0:
            dutyLeft = rampMotor(dutyLeft, i)
            leftMotor0.ChangeDutyCycle(dutyLeft)  # Tell motor to what it supposed to do.
            # leftMotor1.ChangeDutyCycle(dutyLeft)
            # leftMotor2.ChangeDutyCycle(dutyLeft)
            print("The current i value is {}. The current duty percent is {}. Remaining time is {}".format(i, dutyLeft,
                                                                                                           currTime))
            currTime = currTime - 1;
            time.sleep(0.5);
        print(" ")

while True or KeyboardInterrupt:

    # Check for joystick events
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                print("button 0 down")
            if event.button == 1:
                print("button 1 down")
            if event.button == 2:
                print("button 2 down")
            if event.button == 3:
                print("button 3 down")
            if event.button == 4:
                print("button 4 down")
            if event.button == 5:
                print("button 5 down")
            if event.button == 6:
                print("button 6 down")
            if event.button == 7:
                print("button 7 down")
            if event.button == 8:
                print("button 8 down")
            if event.button == 9:
                print("button 9 down")
            if event.button == 10:
                print("button 10 down")
            if event.button == 11:  # Middle Right Button
                print("button 11 down")
                os.system("systemctl poweroff")

        # while True:
        #     for i in range(10000):
        #         rightMotor1.ChangeDutyCycle(cycle)
        #         time.sleep(1)
        #         cycle = cycle + 0.001
        #         print(cycle)
        #     for i in range(10000):
        #         rightMotor1.ChangeDutyCycle(cycle)
        #         time.sleep(1)
        #         cycle = cycle - .001
        #         print(cycle)

        if event.type == pygame.JOYAXISMOTION:
            if event.axis < 2:  # Controls for Left Motor
                if event.axis == 1:
                    if (event.value >= -0.01) and (event.value <= 0.09):
                        dutyLeft = offset
                    else:
                        dutyLeft = -6 * event.value + offset
                    leftMotor0.ChangeDutyCycle(dutyLeft)
                    # leftMotor1.ChangeDutyCycle(dutyLeft)
                    # leftMotor2.ChangeDutyCycle(dutyLeft)
                    print(dutyLeft)

            if event.axis == 2 or event.axis == 3:  # Controls for Right Motor, 2: Left/Right, 3: Up/Down
                if event.axis == 3:
                    if (event.value >= -0.01) and (event.value <= 0.09):
                        dutyRight = offset
                    else:
                        dutyRight = 6 * event.value + offset
                    rightMotor0.ChangeDutyCycle(dutyRight)
                    # rightMotor1.ChangeDutyCycle(dutyRight)
                    # rightMotor2.ChangeDutyCycle(dutyRight)
                    print(event.value)

