### Start Old Functions ###
def rampMotor(curr, target):
    # Converts -1<x<1 xbox signal to a ramped value for the pwm control
    # Inputs    : curr - current pwm value for the desired motor
    #           : target - -1<x<1 xbox signal to get modified
    # Outputs   : new - ramped signal

    offset = 30
    tempNew = newDutyCycleValue(target)

    # tempNew - Dummy variable for converted Target value

    # Right now the signal has been converted to a percentage
    # It will now get ramped
    stepValue = 1;
    if abs((tempNew) - (curr)) >= stepValue:    # If the distance between the current and desired is > 1
        if tempNew > curr:                       # If the value of the desired duty is greater than the current value
            new = curr + stepValue                # Set output to current value + 1
        else:                                    # If the value of the desired is less than the current value
            new = curr - stepValue                # Set output to current value - 1
    else:                                       # If the value is does not exceed the step
        new = tempNew                            # Set output to tempNew

    return new  # Send the output


def wait4XboxControllerOLD():
    # Loop to ensure X-Box controller connection
    # Function has no inputs and no outputs
    while True:         # Loop runs until a connection is found
        try:            # Code will attempt to run this section
            joysticks = []      # Initialize joystick variable
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
### End Old Functions ###


def presetRampProgram():
    # Loop to Verify Outputs
    while True:
        # offset = 30   &   cycle = 30
        # 20% - Full Reverse    =       Rover Goes forwards
        # 30% - Stopped         =       Rover is not moving
        # 40% - Full Forward    =       Rover goes backwards
        dutyLeft = 40  # Initialize left duty cycle
        for i in [-1, 0, 1, 0]:  # Run loop for the values [-1,0,1,0]
            currTime = 20  # Set duration of ramp cycle
            while currTime >= 0:
                dutyLeft = newDutyCycleValue(i)
                leftMotor0.ChangeDutyCycle(dutyLeft)  # Tell motor to what it supposed to do.
                # leftMotor1.ChangeDutyCycle(dutyLeft)
                # leftMotor2.ChangeDutyCycle(dutyLeft)
                print(
                    "The current i value is {i}. The current duty percent is {dutyLeft}. Remaining time is {currTime}")
                currTime = currTime - 1
                time.sleep(1)
            print(" ")
