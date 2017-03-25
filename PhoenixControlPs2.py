# Project Lynxmotion Phoenix
# Description: Phoenix, control file.
# 		The control input subroutine for the phoenix software is placed in this file.
# 		Can be used with V2.0 and above
# Configuration version: V1.0
# Date: 25-10-2009
# Programmer: Jeroen Janssen (aka Xan)
# 
# Hardware setup: PS2 version
# 
# NEW IN V1.0
# 	- First Release
# 
# 	Walk method 1:
# 	- Left Stick	Walk/Strafe
# 	- Right Stick	Rotate
# 
# 	Walk method 2:
# 	- Left Stick	Disable
# 	- Right Stick	Walk/Rotate
# 
# 
# PS2 CONTROLS:
# 	[Common Controls]
# 	- Start			Turn on/off the bot
# 	- L1			Toggle Shift mode
# 	- L2			Toggle Rotate mode
# 	- Circle		Toggle Single leg mode
#    - Square        Toggle Balance mode
# 	- Triangle		Move body to 35 mm from the ground (walk pos) 
# 					and back to the ground
# 	- D-Pad up		Body up 10 mm
# 	- D-Pad down	Body down 10 mm
# 	- D-Pad left	decrease speed with 50mS
# 	- D-Pad right	increase speed with 50mS
# 
# 	[Walk Controls]
# 	- select		Switch gaits
# 	- Left Stick	(Walk mode 1) Walk/Strafe
# 				 	(Walk mode 2) Disable
# 	- Right Stick	(Walk mode 1) Rotate, 		
# 					(Walk mode 2) Walk/Rotate
# 	- R1			Toggle Double gait travel speed
# 	- R2			Toggle Double gait travel length
# 
# 	[Shift Controls]
# 	- Left Stick	Shift body X/Z
# 	- Right Stick	Shift body Y and rotate body Y
# 
# 	[Rotate Controls]
# 	- Left Stick	Rotate body X/Z
# 	- Right Stick	Rotate body Y	
# 
# 	[Single leg Controls]
# 	- select		Switch legs
# 	- Left Stick	Move Leg X/Z (relative)
# 	- Right Stick	Move Leg Y (absolute)
# 	- R2			Hold/release leg position
# 
# 	[GP Player Controls]
# 	- select		Switch Sequences
# 	- R2			Start Sequence
# 
# ====================================================================
import wiringpi
from Gait import cTravelDeadZone, cRF, GaitSelect, LegLiftHeight

# [CONSTANTS]
WalkMode = 0
TranslateMode = 1
RotateMode = 2
SingleLegMode = 3
GPPlayerMode = 4
# --------------------------------------------------------------------
# [PS2 Physical Pins The Controller Is Connected To]
PS2DAT = 21  # PS2 Controller DAT (Brown)
PS2CMD = 19  # PS2 controller CMD (Orange)
PS2SEL = 24  # PS2 Controller SEL (Blue)
PS2CLK = 23  # PS2 Controller CLK (White)
PadMode = 0x79  # $79
CLK_DELAY = 1  # 4
# --------------------------------------------------------------------
# [Ps2 Controller Variables]
DualShock = [None] * 7
LastButton = [None] * 2
DS2Mode = None
PS2Index = None
BodyYOffset = None
BodyYShift = None
ControlMode = None
DoubleHeightOn = None
DoubleTravelOn = None
WalkMethod = None
# --------------------------------------------------------------------
# [PS2 GPIO Pins The Controller Is Connected To As Used By WirinPi]
_commandPin = None
_dataPin = None
_clkPin = None
_attnPin = None

_IsWiringpiInitialised = False


# --------------------------------------------------------------------
# [InitController] Initialize the PS2 controller
def InitController():
    global _dataPin, _attnPin, _clkPin, _commandPin, BodyYOffset, BodyYShift, DS2Mode, _IsWiringpiInitialised
    _attempts = 10

    if not _IsWiringpiInitialised:
        _IsWiringpiInitialised = True
        if wiringpi.wiringPiSetupGpio() == -1:
            print ("Unable to start wiringPi\n")
            return False

    _commandPin = wiringpi.physPinToGpio(PS2CMD)
    _dataPin = wiringpi.physPinToGpio(PS2DAT)
    _clkPin = wiringpi.physPinToGpio(PS2CLK)
    _attnPin = wiringpi.physPinToGpio(PS2SEL)

    wiringpi.pinMode(_commandPin, wiringpi.OUTPUT)  # Set command pin to output
    wiringpi.pinMode(_dataPin, wiringpi.INPUT)  # Set data pin to input
    wiringpi.pullUpDnControl(_dataPin, wiringpi.PUD_UP)  # activate PI internal pulldown resistor
    wiringpi.pinMode(_attnPin, wiringpi.OUTPUT)  # Set attention pin to output
    wiringpi.pinMode(_clkPin, wiringpi.OUTPUT)  # Set clock pin to output

    while DS2Mode != PadMode and _attempts > 0:
        wiringpi.digitalWrite(_clkPin, 1)  # high PS2CLK

        LastButton[0] = 255
        LastButton[1] = 255
        BodyYOffset = 0
        BodyYShift = 0

        # wiringpi.digitalWrite(_clkPin, 0)   # low PS2SEL
        # DS2Mode = transmitBytes(0x01)        # shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$1\8]
        # shiftin PS2DAT,PS2CLK,FASTLSBPOST,[DS2Mode\8]
        buf = transmitBytes([0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00])
        DS2Mode = buf[1]
        wiringpi.delay(1)  # pause 1

        print("DS2Mode=0x%0x, PadMode=0x%0x" % (DS2Mode, PadMode))
        transmitBytes([0x01, 0x43, 0x00, 0x01, 0x00])  # CONFIG_MODE_ENTER0
        transmitBytes([0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00])  # SET_MODE_AND_LOCK
        transmitBytes([0x01, 0x4F, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x00, 0x00])  # SET_DS2_NATIVE_MODE
        transmitBytes([0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A])  # CONFIG_MODE_EXIT_DS2_NATIVE
        transmitBytes([0x01, 0x43, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # CONFIG_MODE_EXIT

        _attempts -= 1
        # sound P9,[100\4000, 100\4500, 100\5000]

    if DS2Mode != PadMode:
        return False

    # goto InitController # Check if the remote is initialized correctly
    return True


# --------------------------------------------------------------------
# [ControlInput] reads the input data from the PS2 controller and processes the
# data to the parameters.
def ControlInput():
    global HexOn, Prev_HexOn, BodyPosX, BodyPosY, BodyPosZ, BodyRotX, BodyRotY, BodyRotZ, \
        TravelLengthX, TravelLengthZ, TravelRotationY, BodyYOffset, BodyYShift, SelectedLeg, \
        ControlMode, BalanceMode, SpeedControl, GaitType, DoubleTravelOn, WalkMethod, \
        DoubleHeightOn, GPStart, SLHold, GPSeq, LegLiftHeight

    print("ControlInput: LB0=%0x, LB1=%0x\n" % LastButton[0], LastButton[1])

    DualShock[0:7] = transmitBytes([0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00])
    wiringpi.delay(10)

    #  Switch bot on/off
    if (DualShock[1] & 0x08 == 0) and LastButton[0] & 0x08:  # Start Button test bit3
        print("Start button: HexOn=%d, Prev_HexOn=%d\n" % HexOn, Prev_HexOn)
        if HexOn:
            # Turn off
            BodyPosX = 0
            BodyPosY = 0
            BodyPosZ = 0
            BodyRotX = 0
            BodyRotY = 0
            BodyRotZ = 0
            TravelLengthX = 0
            TravelLengthZ = 0
            TravelRotationY = 0
            BodyYOffset = 0
            BodyYShift = 0
            SelectedLeg = 255

            HexOn = 0
        else:
            # Turn on
            HexOn = 1
            # endif
    # endif

    if HexOn:
        # [SWITCH MODES]

        # Translate mode
        if (DualShock[2] & 0x04 == 0) and LastButton[1] & 0x04:  # L1 Button test bit2
            # sound p9, [50\4000]
            if ControlMode != TranslateMode:
                ControlMode = TranslateMode
            else:
                if SelectedLeg == 255:
                    ControlMode = WalkMode
                else:
                    ControlMode = SingleLegMode
                    # endif
                    # endif
        # endif

        # Rotate mode
        if (DualShock[2] & 0x01 == 0) and LastButton[1] & 0x01:  # L2 Button test bit0
            # sound p9, [50\4000]
            if ControlMode != RotateMode:
                ControlMode = RotateMode
            else:
                if SelectedLeg == 255:
                    ControlMode = WalkMode
                else:
                    ControlMode = SingleLegMode
                    # endif
                    # endif
        # endif

        # Single leg mode
        if (DualShock[2] % 0x20 == 0) and LastButton[1] & 0x20:  # Circle Button test bit5
            if abs(TravelLengthX) < cTravelDeadZone and abs(TravelLengthZ) < cTravelDeadZone and abs(
                            TravelRotationY * 2) < cTravelDeadZone:
                # Sound P9,[50\4000]
                if ControlMode != SingleLegMode:
                    ControlMode = SingleLegMode
                    if SelectedLeg == 255:  # Select leg if none is selected
                        SelectedLeg = cRF  # Startleg
                else:
                    ControlMode = WalkMode
                    SelectedLeg = 255
                    # endif
                    # endif
        # endif

        # GP Player mode
        if (DualShock[2] & 0x40 == 0) and LastButton[1] & 0x40:  # Cross Button test bit6
            # Sound P9,[50\4000]
            if ControlMode != GPPlayerMode:
                ControlMode = GPPlayerMode
                GPSeq = 0
            else:
                ControlMode = WalkMode
                # endif
        # endif

        # [Common functions]
        # Switch Balance mode on/off
        if (DualShock[2] & 0x80 == 0) and LastButton[1] & 0x80:  # Square Button test bit7
            BalanceMode ^= 1
            if BalanceMode:
                # sound P9,[250\3000]
                pass
            else:
                # sound P9,[100\4000, 50\8000]
                pass
                # endif
        # endif

        # Stand up, sit down
        if (DualShock[2] & 0x10 == 0) and LastButton[1] & 0x10:  # Triangle Button test bit4
            if BodyYOffset > 0:
                BodyYOffset = 0
            else:
                BodyYOffset = 35
                # endif
        # endif

        if (DualShock[1] & 0x10 == 0) and LastButton[0] & 0x10:  # D-Up Button test bit4
            BodyYOffset += 10
        # endif

        if (DualShock[1] & 0x40 == 0) and LastButton[0] & 0x40:  # D-Down Button test bit6
            BodyYOffset -= 10
        # endif

        if (DualShock[1] & 0x20 == 0) and LastButton[0] & 0x20:  # D-Right Button test bit5
            if SpeedControl > 0:
                SpeedControl -= 50
                # sound p9, [50\4000]
                # endif
        # endif

        if (DualShock[1] & 0x80 == 0) and LastButton[0] & 0x80:  # D-Left Button test bit7
            if SpeedControl < 2000:
                SpeedControl += 50
                # sound p9, [50\4000]
                # endif
        # endif

        # [Walk functions]
        if ControlMode == WalkMode:
            # Switch gates
            if ((DualShock[1] & 0x01 == 0) and LastButton[0] & 0x01  # Select Button test bit0
                    and abs(TravelLengthX) < cTravelDeadZone  # No movement
                    and abs(TravelLengthZ) < cTravelDeadZone
                    and abs(TravelRotationY * 2) < cTravelDeadZone):
                if GaitType < 7:
                    # Sound P9,[50\4000]
                    GaitType += 1
                else:
                    # Sound P9,[50\4000, 50\4500]
                    GaitType = 0
                # endif

                # Sound P9,[50\4000+Gaittype*500]
                # DTMFOUT2 9,[GaitType]
                GaitSelect()
            # endif

            # Double leg lift height
            if (DualShock[2] & 0x08 == 0) and LastButton[1] & 0x08:  # R1 Button test bit3
                # sound p9, [50\4000]
                DoubleHeightOn ^= 1
                if DoubleHeightOn:
                    LegLiftHeight = 80
                else:
                    LegLiftHeight = 50
                    # endif
            # endif

            # Double Travel Length
            if (DualShock[2] & 0x02 == 0) and LastButton[1] & 0x02:  # R2 Button test bit1
                # sound p9, [50\4000]
                DoubleTravelOn ^= 1
            # endif

            #  Switch between Walk method 1 and Walk method 2
            if (DualShock[1] & 0x04 == 0) and LastButton[0] & 0x04:  # R3 Button test bit2
                # sound p9, [50\4000]
                WalkMethod ^= 1
            # endif

            # Walking
            if WalkMethod:  # (Walk Methode)
                TravelLengthZ = (DualShock[4] - 128)  # Right Stick Up/Down
            else:
                TravelLengthX = -(DualShock[5] - 128)
                TravelLengthZ = (DualShock[6] - 128)
            # endif

            if DoubleTravelOn == 0:  # (Double travel length)
                TravelLengthX /= 2
                TravelLengthZ /= 2
            # endif

            TravelRotationY = -(DualShock[3] - 128) / 4  # Right Stick Left/Right
        # endif

        # [Translate functions]
        # BodyYShift = 0
        if ControlMode == TranslateMode:
            BodyPosX = (DualShock[5] - 128) / 2
            BodyPosZ = -(DualShock[6] - 128) / 3
            BodyRotY = (DualShock[3] - 128) / 6
            BodyYShift = (-(DualShock[4] - 128) / 2)
        # endif

        # [Rotate functions]
        if ControlMode == RotateMode:
            BodyRotX = (DualShock[6] - 128) / 8
            BodyRotY = (DualShock[3] - 128) / 6
            BodyRotZ = (DualShock[5] - 128) / 8
            BodyYShift = (-(DualShock[4] - 128) / 2)
        # endif

        # [Single leg functions]
        if ControlMode == SingleLegMode:

            # Switch leg for single leg control
            if (DualShock[1] & 0x01 == 0) and LastButton[0] & 0x01:  # Select Button test bit0
                # Sound P9,[50\4000]
                if SelectedLeg < 5:
                    SelectedLeg += 1
                else:
                    SelectedLeg = 0
                    # endif
            # endif

            # Single Leg Mode
            if ControlMode == SingleLegMode:
                SLLegX = (DualShock[5] - 128) / 2  # Left Stick Right/Left
                SLLegY = (DualShock[4] - 128) / 10  # Right Stick Up/Down
                SLLegZ = (DualShock[6] - 128) / 2  # Left Stick Up/Down
            # endif

            #  Hold single leg in place
            if (DualShock[2] & 0x02 == 0) and LastButton[1] & 0x02:  # R2 Button test bit1
                # sound p9, [50\4000]
                SLHold ^= 1
                # endif
        # endif

        # [Single leg functions]
        if ControlMode == GPPlayerMode:

            # Switch between sequences
            if (DualShock[1] & 0x01 == 0) and LastButton[0] & 0x01:  # Select Button test bit0
                if GPStart == 0:
                    if GPSeq < 5:  # Max sequence
                        # sound p9, [50\3000]
                        GPSeq += 1
                    else:
                        # Sound P9,[50\4000, 50\4500]
                        GPSeq = 0
                        # endif
                        # endif
            # endif

            # Start Sequence
            if (DualShock[2] & 0x02 == 0) and LastButton[1] & 0x02:  # R2 Button test bit1
                GPStart = 1
                # endif
        # endif

        # Calculate walking time delay
        InputTimeDelay = 128 - min(abs((DualShock[5] - 128)), abs((DualShock[6] - 128)), abs((DualShock[3] - 128)))

    # endif

    # Calculate BodyPosY
    BodyPosY = min((BodyYOffset + BodyYShift), 0)

    # Store previous state
    LastButton[0] = DualShock[1]
    LastButton[1] = DualShock[2]
    return


# --------------------------------------------------------------------
# Bit bang a single byte.
# Inputs:
# 		byte 	- The byte to transmit.
#
# Returns:
#       The byte received
def transmitByte(byte):
    RXdata = transmitBytes([byte])[0]
    # print("RXdata=0x%x" % RXdata)
    return RXdata


# --------------------------------------------------------------------
# Bit bang a single bit.
# Inputs:
# 		outBit 	- The bit to transmit.
#
# Returns:
#       The bit received.
def transmitBit(outBit):
    # print("write outBit=%d, _commandPin=1" % outBit)
    wiringpi.digitalWrite(_commandPin, outBit)

    # Pull clock low to transfer bit
    wiringpi.digitalWrite(_clkPin, 0)

    # Wait for the clock delay before reading the received bit.
    wiringpi.delayMicroseconds(CLK_DELAY)

    # Read the data pin.
    inBit = wiringpi.digitalRead(_dataPin)

    # Done transferring bit. Put clock back high
    wiringpi.digitalWrite(_clkPin, 1)
    wiringpi.delayMicroseconds(CLK_DELAY)
    return inBit


# --------------------------------------------------------------------
# Bit bang out an entire array of bytes.
#
# Inputs:
# 		bytes 	- Array of bytes to be transmitted.
#
# Returns:
#       The bytes received.
def transmitBytes(outbytes):
    _readDelay = 1

    outBits = reduce(lambda accu, b: accu + b, map(lambda byte: map(lambda s: (byte >> s) & 1, range(8)), outbytes))
    # print(outBits)

    # Ready to begin transmitting, pull attention low.
    wiringpi.digitalWrite(_attnPin, 0)

    inBits = map(lambda bit: transmitBit(bit), outBits)
    # print(inBits)

    # Packet finished, release attention line.
    wiringpi.digitalWrite(_attnPin, 1)

    chunks = [inBits[x:x + 8] for x in range(0, len(inBits), 8)]
    map(lambda chunk: chunk.reverse(), chunks)
    result = map(lambda chunk: reduce(lambda accu, bit: (accu << 1) | bit, chunk), chunks)

    # Wait some time before beginning another packet.
    wiringpi.delay(_readDelay)

    return result
