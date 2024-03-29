# !/usr/bin/env python3
# -- coding: utf-8 -*-

# NOTE: Do not remove above code, it tells the pi what coding language is being used!

# Author - Ethan Leone
# Date - March 31st, 2023

# %% Start Imports ###
import time                 # Allows to pause
import atexit               # "At Exit" module for when code is terminated
# import serial as ser        # Interfaces with the arduino
### End imports ###


# %%####### Start Custom Functions ##########

def formSerialConnection():
    # Function to establish a connection with an arduino using serial connection via a USB cable
    # Inputs  : none
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino

    global uno  # Serial communication variable

    while True:                                                 # Loop until the connection has been established
        try:
            uno = ser.Serial('/dev/ttyACM0', 115200, timeout=0.1)       # Enable arduino communication (pi)
            # Notes for serial function which established the connection:
            # Inputs  : port - String name of the port which the arduino connects to the device
            #           baudWidth - Rate of communication between pi and arduino (MUST be the same on both)
            #           timeout=0.1 - Specifies seconds for the arduino to wait for data
            # Outputs : uno - serial connection between devices
        except:
            print("ERROR : The arudino is not connected to the Pi")     # Inform that the connection has not been made
            time.sleep(0.5)                                             # Wait half a second
        else:
            time.sleep(1.8)                                             # Gives the connection time to finalize
            print("--- Arduino Connection Is Established ---")
            print("-----------------------------------------")
            break


def resetArduino():
    # Function reset the connected arduino and gives a 2-second delay to allow the arduino to finish resetting
    # Inputs  : none
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino

    global uno              # Call the connection
    uno.setDTR(False)       # Set active to false
    time.sleep(0.1)         # Give it 1/10 second to process
    uno.setDTR(True)        # Set active to true
    time.sleep(2)           # Allow uno to run the setup function and start


def setPin(pinCode, pinValue):
    # Tells the arduino to change the mode of a given pin. The data is sent as a 3-digit number, with the first two
    # digits being the pin-number and the final digit being 1 or 0 for high or low
    # Inputs  : pinCode - Number of the pin which will be set
    #           pinValue - New value of the pin
    # Outputs : none
    # Globals : uno - Holds the serial connection to the arduino
    # Example : setPin(10, 0) - Turns off pin 10

    global uno

    if pinCode < 10:
        message = "0" + str(pinCode) + str(pinValue)    # Create output string for pins with one digit
    else:
        message = str(pinCode) + str(pinValue)          # Create output string for pins with two digits

    print(message)

    try:
        uno.write(str(message).encode())                # Try to transmit through serial connection
    except:
        print("Arduino is no longer connected !!!")     # Warn about a disconnection if transmittion fails
        formSerialConnection()                          # Attempt to reconnect to arduino
    else:
        noResponse = 1                                  # Logical variable to know if the arduino has returned a response
        while noResponse:
            data = uno.readline()                       # Read the serial monitor
            if data:                                    # If the serial monitor said anything
                rawData = data.rstrip('\n'.encode('latin-1'))  # Convert monitor to bytes
                print("Arduino: " + rawData.decode('latin-1'))  # Print data
                noResponse = 0                          # Let main code progress


def cleanup():
    # Callback function to disable pins 3-12 on the arduino
    # Inputs  - none
    # Outputs - none
    # Globals : uno - Holds the serial connection to the arduino

    global uno                  # Calls the arduino communication variable

    for pin in range(10):       # Repeat for each pin from front to back
        setPin(pin+3, 0)        # Disable pin

    print("----------------------------")  # Ending display
    try:
        time.sleep(0.5)         # Let arduino disable pins
        resetArduino()          # Restart arduino
        uno.close()             # End arduino communication
    except:
        print("The arduino was no longer connected to disable the pins")
    else:
        print("--- Arduino Disconnected ---")
        print("----------------------------")
    print("---- Program Terminated ----")
    print("----------------------------")


def gCode2num(inputString):
    inputString = inputString.replace(" ", "")
    length = len(inputString)
    [firstChar, secondChar] = inputString[:2]
    if length > 2:
        command = ('%04d' % (int(inputString[2:]))).replace('-', '9')
    else:
        command = '0000'
    if firstChar == 'P':
        comCode = f"1{secondChar}{command}"
    elif firstChar == 'S':
        comCode = f"2{secondChar}{command}"
    elif firstChar == 'Q':
        comCode = f"3{secondChar}{command}"
    elif firstChar == 'M':
        comCode = f"4{secondChar}{command}"
    elif firstChar == 'R':
        comCode = f"5{secondChar}{command}"
    elif firstChar == 'K':
        comCode = f"6{secondChar}{command}"
    elif firstChar == 'H':
        comCode = f"7{secondChar}{command}"
    elif firstChar == 'E':
        comCode = f"8{secondChar}{command}"
    else:
        comCode = "000000"

    return comCode


### End Custom Functions ###

# %%####### Start Main Code ##########

# Initializations
# atexit.register(cleanup)  # Tells the cleanup function to run at close

# # Esatablish connections
# formSerialConnection()  # Connect to arduino
#
# while True:
#     for mode in [1, 0]:
#         for pin in range(10):
#             print(" ")
#             time.sleep(1)
#             startTime = time.time()
#             print("Python: Set pin {} to {}.".format(pin+3, mode))
#             setPin(pin + 3, mode)
#

gCode2num('P2 -350')
gCode2num('S5 13')
gCode2num('Q4')
gCode2num('M4 2042')
gCode2num('R5')
