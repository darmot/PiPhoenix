import sys
import wiringpi
from PS2ControllerConstants import *
from PS2Controller import *
#from wiringPiSPI import *

READDELAYMS = 10

if wiringpi.wiringPiSetupGpio() == -1:
    print ("Unable to start wiringPi: %s\n" % strerror(errno))
    sys.exit(-1)

if wiringPiSPISetup(0, 100000) == -1:
    print("Unable to setup SPI: %s\n" % strerror(errno))
    sys.exit(-1)

commandPin = wiringpi.physPinToGpio(19)
dataPin = wiringpi.physPinToGpio(21)
clkPin = wiringpi.physPinToGpio(23)
attnPin = wiringpi.physPinToGpio(24)
print("commandPin=%d, dataPin=%d, clkPin=%d, attnPin=%d" % (commandPin, dataPin, clkPin, attnPin))

############## PiPS2 stuff ############################
## Create a PIPS2 object
#pips2 = PiPS2()
nextRead = READDELAYMS

#pips2.setupPins(commandPin, dataPin, clkPin, attnPin)
print("Pins setup")

#pips2._readDelay = 1

# put controller in config mode
digitalWrite(commandPin, 1)
digitalWrite(clkPin, 1)
digitalWrite(attnPin, 0)

spiBuffer = [0x01, 0x43, 0x00, 0x01, 0x00];
wiringPiSPIDataRW(0, spiBuffer)
print(spiBuffer.map(lambda x: '0x%x'.format(x)))

digitalWrite(commandPin, 1)
delayMicroseconds(1)
digitalWrite(attnPin, 1)

delayMicroseconds(10)

# put controller inanalogue mode
digitalWrite(commandPin, 1)
digitalWrite(clkPin, 1)
digitalWrite(attnPin, 0)

spiBuffer = [0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00];
wiringPiSPIDataRW(0, spiBuffer)
print(spiBuffer.map(lambda x: '0x%x'.format(x)))

digitalWrite(pips2._commandPin, 1)
delayMicroseconds(1)
digitalWrite(pips2._attnPin, 1)

delayMicroseconds(10)

#exit config mode
digitalWrite(pips2._commandPin, 1)
digitalWrite(pips2._clkPin, 1)
digitalWrite(pips2._attnPin, 0)

spiBuffer = [0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A];
wiringPiSPIDataRW(0, spiBuffer)
print(spiBuffer.map(lambda x: '0x%x'.format(x)))

digitalWrite(pips2._commandPin, 1)
delayMicroseconds(1)
digitalWrite(pips2._attnPin, 1)

delayMicroseconds(10)

# poll controller and check in analogue mode
digitalWrite(pips2._commandPin, 1)
digitalWrite(pips2._clkPin, 1)
digitalWrite(pips2._attnPin, 0)

spiBuffer = [0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
wiringPiSPIDataRW(0, spiBuffer)
print(spiBuffer.map(lambda x: '0x%x'.format(x)))

chk_ana = spiBuffer[1]

digitalWrite(pips2._commandPin, 1)
delayMicroseconds(1)
digitalWrite(pips2._attnPin, 1)

delayMicroseconds(10)

print("chk_ana=0x%x" % chk_ana)


# Read controller a few times to check if it is talking.
#pips2.readPS2()
#pips2.readPS2()

print("Initialized ...")

#pips2.transmitCmdString(enterConfigMode, len(enterConfigMode))
#pips2.transmitCmdString(setModeAnalogLockMode, len(setModeAnalogLockMode))




