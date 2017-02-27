from PS2Controller_h import *
from wiringpi import *
#from wiringpispi import *


#include <wiringPi.h>
#include <stdio.h>

class PiPS2:

    def __init__(self):
        #private members:
        self._controllerMode = -1
        self._commandPin = -1
        self._dataPin = -1
        self._attnPin = -1
        self._clkPin = -1
        self._readDelay = 0
        self._btnLastState = [0] * 2
        self._btnChangedState = [0] * 2
        self.PS2data = [0] * 21
        self._last_read = 0

    # Initialize the I/O pins.
    def setupPins(self, _commandPin, _dataPin, _clkPin, _attnPin):
        # INITIALIZE I/O
        self._commandPin = _commandPin
        self._dataPin = _dataPin
        self._clkPin = _clkPin
        self._attnPin = _attnPin
        self._controllerMode = ANALOGMODE
        # Set command pin to output
        pinMode(self._commandPin, OUTPUT)
        # Set data pin to input
        pinMode(self._dataPin, INPUT)
        pullUpDnControl(self._dataPin, PUD_UP)
        # Set attention pin to output
        pinMode(self._attnPin, OUTPUT)
        # Set clock pin to output
        pinMode(self._clkPin, OUTPUT)

    # Initialize the I/O pins and set up the controller for the desired mode.
    #	TODO:
    #		This function is hard coded to configure controller for analog mode.
    #		Must also implement input parameters to choose what mode to use.
    # 		If you want digital mode or analog mode with all pressures then use reInitController()
    #	Inputs:
    # 			--!! NOTE !!-- wiringPiSetupPhys(), wiringPiSetupGpio() OR wiringPiSetup()
    # 				should be called first. The following pins refer to either the gpio or the
    #				physical pins, depending on how wiring pi was set up.
    # 	_commandPin - The RPi pin that is connected to the COMMAND line of PS2 remote
    #  	_dataPin	- The RPi pin that is connected to the DATA line of PS2 remote
    #  	_clkPin		- The RPi pin that is connected to the CLOCK line of PS2 remote
    # 	_attnPin	- The RPi pin that is connected to the ATTENTION line of PS2 remote
    #	Returns:
    #		1 -		Config success.
    #		0 - 	Controller is not responding.
    def initializeController(self, _commandPin, _dataPin, _clkPin, _attnPin):

        self.setupPins(_commandPin, _dataPin, _clkPin, _attnPin)

        self._readDelay = 1

        # Set command pin and clock pin high, ready to initialize a transfer.
        digitalWrite(self._commandPin, 1)
        digitalWrite(self._clkPin, 1)

        # Read controller a few times to check if it is talking.
        self.readPS2()
        self.readPS2()

        # Initialize the read delay to be 1 millisecond.
        # Increment read_delay until controller accepts commands.
        # This is a but of dynamic debugging. Read delay usually needs to be about 2.
        # But for some controllers, especially wireless ones it needs to be a bit higher.

        # Try up until readDelay = MAX_READ_DELAY
        while 1:

            # Transmit the enter config command.
            self.transmitBytes(enterConfigMode)

            # Set mode to analog mode and lock it there.
            self.transmitBytes(setModeAnalogLockMode)

            #delay(CMD_DELAY);

            # Return all pressures
            #self.transmitBytes(setAllPressureMode)
            # Exit config mode.
            self.transmitBytes(exitConfigMode)

            # Attempt to read the controller.
            self.readPS2()

            # If read was successful (controller indicates it is in analog mode), break this config loop.
            if self.PS2data[1] == self._controllerMode:
                break

            # If we have tried and failed 10 times. call it quits,
            if self._readDelay == MAX_READ_DELAY:
                return 1


            # Otherwise increment the read delay and go for another loop
            self._readDelay = self._readDelay + 1

        return 0


    # Bit bang a single byte.
    # Inputs:
    # 		byte 	- The byte to transmit.
    #
    # Returns:
    #       The byte received
    def transmitByte(self, byte):
        RXdata = self.transmitBytes([byte])[0]
        #print("RXdata=0x%x" % RXdata)
        return RXdata


    # Bit bang a single bit.
    # Inputs:
    # 		outBit 	- The bit to transmit.
    #
    # Returns:
    #       The bit received.
    def transmitBit(self, outBit):

        # print("write outBit=%d, _commandPin=1" % outBit)
        digitalWrite(self._commandPin, outBit)

        # Pull clock low to transfer bit
        digitalWrite(self._clkPin, 0)

        # Wait for the clock delay before reading the received bit.
        delayMicroseconds(CLK_DELAY)

        # Read the data pin.
        inBit = digitalRead(self._dataPin)

        # Done transferring bit. Put clock back high
        digitalWrite(self._clkPin, 1)
        delayMicroseconds(CLK_DELAY)
        return inBit


    # Bit bang out an entire array of bytes.
    #
    # Inputs:
    # 		bytes 	- Array of bytes to be transmitted.
    #
    # Returns:
    #       The bytes received.
    def transmitBytes(self, bytes):

        outBits = reduce(lambda accu,b: accu + b, map(lambda byte: map(lambda x: CHK(byte, x), range(8)), bytes))
        #print(outBits)

        # Ready to begin transmitting, pull attention low.
        digitalWrite(self._attnPin, 0)

        inBits = map(lambda bit: self.transmitBit(bit), outBits)
        #print(inBits)

        # Packet finished, release attention line.
        digitalWrite(self._attnPin, 1)

        chunks = [inBits[x:x + 8] for x in range(0, len(inBits), 8)]
        map(lambda chunk: chunk.reverse(), chunks)
        result = map(lambda chunk: reduce(lambda accu,bit: (accu<<1)|bit, chunk), chunks)

        # Wait some time before beginning another packet.
        delay(self._readDelay)

        return result


    # Read the PS2 Controller. Save the returned data to PS2data.
    def readPS2(self):

        #print("self._last_read=%s" % self._last_read)
        #print("millis()=%s" % millis())
        timeSince = millis() - self._last_read
        #print("timeSince=%s" % timeSince)

        if timeSince > 1500:        #waited too long
            print("waited too long")
            self.reInitializeController(self._controllerMode)

        if timeSince < self._readDelay:   #waited too short
            print("waited too short")
            delay(self._readDelay - timeSince)

        # Ensure that the command bit is high before lowering attention.
        digitalWrite(self._commandPin, 1)
        # Ensure that the clock is high.
        digitalWrite(self._clkPin, 1)
        # Drop attention pin.
        digitalWrite(self._attnPin, 0)

        # Wait for a while between transmitting bytes so that pins can stabilize.
        delayMicroseconds(BYTE_DELAY)

        # The TX and RX buffer used to read the controller.
        TxRx1 = [0x01,0x42,0,0,0,0,0,0,0]
        TxRx2 = [0,0,0,0,0,0,0,0,0,0,0,0]

        # Grab the first 9 bits
        for i in range(9):
            self.PS2data[i] = self.transmitByte(TxRx1[i])

        print("PS2data: [%s]" % ', '.join(map(lambda x: '0x%0x' % x, self.PS2data)))
        # print("PS2data:")
        # for i in range(21):
        #     print(" %d" % self.PS2data[i])
        # print("\n")

        # If controller is in full data return mode, get the rest of data
        if self.PS2data[1] == 0x79:
            for i in range(12):
                self.PS2data[i+9] = self.transmitByte(TxRx2[i])
                print("%d: %d\t->\t%d\n" % (i, TxRx1[i], self.PS2data[i]))

        print("XXX")

        # Done reading packet, release attention line.
        digitalWrite(self._attnPin, 1)
        self._last_read = millis()

        # Detect which buttons have been changed
        self._btnChangedState[0] = self.PS2data[3] ^ self._btnLastState[0]
        self._btnChangedState[1] = self.PS2data[4] ^ self._btnLastState[1]
        # Save the current button states as the last state for next read)
        self._btnLastState[0] = self.PS2data[3]
        self._btnLastState[1] = self.PS2data[4]



    # Re-Initialize the I/O pins and set up the controller for the desired mode.
    #	TODO:
    #		Currently this function is only coded for either analog mode without all pressures
    # 		returned or analog mode with all pressures. Need to implement digital.
    #	Inputs:
    # 			--!! NOTE !!-- wiringPiSetupPhys(), wiringPiSetupGpio() OR wiringPiSetup()
    # 				should be called first. The following pins refer to either the gpio or the
    #				physical pins, depending on how wiring pi was set up.
    # 	_commandPin - The RPi pin that is connected to the COMMAND line of PS2 remote
    #  	_dataPin	- The RPi pin that is connected to the DATA line of PS2 remote
    #  	_clkPin		- The RPi pin that is connected to the CLOCK line of PS2 remote
    # 	_attnPin	- The RPi pin that is connected to the ATTENTION line of PS2 remote
    #
    # Returns:
    # 		 1 			- Success!
    # 		-1 			- Invalid mode!
    # 		-2 			- Failed to get controller into desired mode in less than MAX_INIT_ATTEMPT attempts
    def reInitializeController(self, _controllerMode):

        print("reInitializeController %x" % _controllerMode)
        self._controllerMode = _controllerMode
        if self._controllerMode != ANALOGMODE and self._controllerMode != ALLPRESSUREMODE:
            return -1

        for initAttempts in range(1, MAX_INIT_ATTEMPT):
            print("attempt #%i" % initAttempts)
            self.transmitBytes(enterConfigMode)
            self.transmitBytes(setModeAnalogLockMode)
            if self._controllerMode == ALLPRESSUREMODE:
                self.transmitBytes(setAllPressureMode)
            self.transmitBytes(exitConfigMode)
            self.readPS2()
            if self.PS2data[1] == self._controllerMode:
                return 1
            delay(self._readDelay)

        return -2


    # Request the changed states data. To determine what buttons have changed states since last read.
    #
    # Input:
    # 		outputChangedStates 	- The pointer to a two element char vector to hold the changed states.
    #
    def getChangedStates(self, outputChangedStates):
        outputChangedStates[0] = self._btnChangedState[0]
        outputChangedStates[1] = self._btnChangedState[1]


