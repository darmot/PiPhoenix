##
# Sample program for PiPS2 library.
# Compile: g++ sample.cpp PiPS2.cpp -o sample -lwiringPi
#
# Sets up the PS2 remote for analog mode and to return all pressure values.
# Reads controller every 10ms and prints the buttons that are pressed to the console.
# BTN_START uses the functionality to detect a button push or release.
# Holding R2 will print the pressure values of the right analog stick to console.
# All other buttons just cause a message to be printed after every read if they are being pressed.
#
# You can just implement the same functionality from the Start button or from the R2 functionality
# for any keys.
#
##
import sys
import wiringpi
from PS2Controller import *

READDELAYMS = 10
EXIT_FAILURE = 1

last_read = 0

def main(argc, argv):
    progname = argv[0]
    argc = argc -1

    if wiringpi.wiringPiSetupGpio() == -1:
        print ( "Unable to start wiringPi: %s\n" % strerror(errno))
        return 1

    commandPin = wiringpi.physPinToGpio(19)
    dataPin = wiringpi.physPinToGpio(21)
    clkPin = wiringpi.physPinToGpio(23)
    attnPin = wiringpi.physPinToGpio(24)

    print("self._last_read=%s" % last_read)
    print("millis()=%s" % millis())
    timeSince = millis() - last_read
    print("timeSince=%s" % timeSince)

    ############## PiPS2 stuff ############################
    ## Create a PIPS2 object
    pips2 = PiPS2()
    nextRead = READDELAYMS
    if not pips2.initializeController(commandPin, dataPin, clkPin, attnPin):
        print("%s: Failed to configure gamepad\nController is not responding.\nExiting ...\n" % progname)
        exit(EXIT_FAILURE)

    print("Initialized ...")

    returnVal = pips2.reInitializeController(ALLPRESSUREMODE)
    if returnVal == -1:
        print("%s: Invalid Mode\n" % progname)
        exit(EXIT_FAILURE)
    elif returnVal == -2:
        print("%s: Took too many tries to reinit.\n" % progname)
        exit(EXIT_FAILURE)

    delay(50);
    print("Control mode = 0x%0x\n" % pips2.PS2data[1])

    while (1):
        if millis() > nextRead:
            nextRead = nextRead + READDELAYMS
            # Read the controller.
            pips2.readPS2()

            # Example detecting when a button is pressed or released.
            changedStates = pips2.getChangedStates()  # Populate the vector
            btnDowns = [0] * 2                     # Create the vector of buttons that have been pushed since last read.
            btnUps = [0] * 2	                   # Create the vector of buttons that have been pushed since last read.
            # Buttons that have been pushed down are buttons that are currently down and have changed.
            btnDowns[0] = ~pips2.PS2data[3] & changedStates[0]
            # Buttons that have been released are buttons that are currently up and have changed.
            btnUps[0] = pips2.PS2data[3] & changedStates[0]

            # Just going to check for the START button.
            if CHK(btnDowns[0], BTN_START):
                print("BTN_START has been pushed DOWN\n")
            if CHK(btnUps[0], BTN_START):
                print("BTN_START has been RELEASED\n")


            # Example reading each button.
            if not CHK(pips2.PS2data[3], BTN_SELECT):
                print("BTN_SELECT is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_RIGHT_JOY):
                print("BTN_RIGHT_JOY is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_LEFT_JOY):
                print("BTN_LEFT_JOY is pressed\n")
            #if not CHK(pips2.PS2data[3], BTN_START):
            #	print("BTN_START is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_UP):
                print("BTN_UP is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_RIGHT):
                print("BTN_RIGHT is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_DOWN):
                print("BTN_DOWN is pressed\n")
            if not CHK(pips2.PS2data[3], BTN_LEFT):
                print("BTN_LEFT is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_L2):
                print("BTN_L2 is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_R2):
                print("Right Joy   Horizontal = %d\tVertical = %d\n" % (pips2.PS2data[5], pips2.PS2data[6]))
            if not CHK(pips2.PS2data[4], BTN_L1):
                print("BTN_L1 is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_R1):
                print("BTN_R1 is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_TRIANGLE):
                print("BTN_TRIANGLE is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_CIRCLE):
                print("BTN_CIRCLE is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_X):
                print("X is pressed\n")
            if not CHK(pips2.PS2data[4], BTN_SQUARE):
                print("BTN_SQUARE is pressed\n")


    return 0

main(len(sys.argv), sys.argv)
