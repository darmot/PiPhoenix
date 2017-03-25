import sys
import wiringpi
from PS2ControllerConstants import *
from PS2Controller import *

READDELAYMS = 10

def printHexArray(hexArray):
    print("Antwort: [%s]" % ', '.join(map(lambda x: '0x%0x' % x, hexArray)))
    return

if wiringpi.wiringPiSetupGpio() == -1:
    print ("Unable to start wiringPi: %s\n" % strerror(errno))
    sys.exit(-1)

commandPin = wiringpi.physPinToGpio(19)
dataPin = wiringpi.physPinToGpio(21)
clkPin = wiringpi.physPinToGpio(23)
attnPin = wiringpi.physPinToGpio(24)
print("_commandPin=%d, _dataPin=%d, _clkPin=%d, _attnPin=%d" % (commandPin, dataPin, clkPin, attnPin))

############## PiPS2 stuff ############################
## Create a PIPS2 object
pips2 = PiPS2()
nextRead = READDELAYMS

pips2.setupPins(commandPin, dataPin, clkPin, attnPin)
print("Pins setup")

pips2._readDelay = 1

# put controller in config mode
digitalWrite(pips2._commandPin, 1)
digitalWrite(pips2._clkPin, 1)
digitalWrite(pips2._attnPin, 1)
delayMicroseconds(1000)

answer = pips2.transmitByte(0x01)
print("Antwort: 0x%0x" % answer)

answer = pips2.transmitBytes([0x01, 0x42, 0x00, 0x00, 0x00])
printHexArray(answer)

answer = pips2.transmitBytes([0x01, 0x42, 0x00, 0x00, 0x00])
printHexArray(answer)

answer = pips2.transmitByte(0x01)
print("Antwort: 0x%0x" % answer)

#sys.exit(0)

# CONFIG_MODE_ENTER
answer = pips2.transmitBytes([0x01, 0x43, 0x00, 0x01, 0x00])
printHexArray(answer)

# SET_MODE_AND_LOCK
answer = pips2.transmitBytes([0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00])
printHexArray(answer)

# SET_DS2_NATIVE_MODE
answer = pips2.transmitBytes([0x01, 0x4F, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x00, 0x00])

# CONFIG_MODE_EXIT_DS2_NATIVE
answer = pips2.transmitBytes([0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A])

# CONFIG_MODE_EXIT
answer = pips2.transmitBytes([0x01, 0x43, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
printHexArray(answer)

# poll controller and check in analogue mode
answer = pips2.transmitBytes([0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
printHexArray(answer)
chk_ana = answer[1]
print("chk_ana=0x%x" % chk_ana)


# Read controller a few times to check if it is talking.
#pips2.readPS2()
#pips2.readPS2()

print("Initialized ...")

#pips2.transmitCmdString(enterConfigMode, len(enterConfigMode))
#pips2.transmitCmdString(setModeAnalogLockMode, len(setModeAnalogLockMode))




