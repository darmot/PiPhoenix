#Project Lynxmotion Phoenix
#Description: Phoenix, control file.
#		The control input subroutine for the phoenix software is placed in this file.
#		Can be used with V2.0 and above
#Configuration version: V1.0
#Date: 25-10-2009
#Programmer: Jeroen Janssen (aka Xan)
#
#Hardware setup: PS2 version
#
#NEW IN V1.0
#	- First Release
#
#	Walk method 1:
#	- Left Stick	Walk/Strafe
#	- Right Stick	Rotate
#
#	Walk method 2:
#	- Left Stick	Disable
#	- Right Stick	Walk/Rotate
#
#
#PS2 CONTROLS:
#	[Common Controls]
#	- Start			Turn on/off the bot
#	- L1			Toggle Shift mode
#	- L2			Toggle Rotate mode
#	- Circle		Toggle Single leg mode
#   - Square        Toggle Balance mode
#	- Triangle		Move body to 35 mm from the ground (walk pos)
#					and back to the ground
#	- D-Pad up		Body up 10 mm
#	- D-Pad down	Body down 10 mm
#	- D-Pad left	decrease speed with 50mS
#	- D-Pad right	increase speed with 50mS
#
#	[Walk Controls]
#	- select		Switch gaits
#	- Left Stick	(Walk mode 1) Walk/Strafe
#				 	(Walk mode 2) Disable
#	- Right Stick	(Walk mode 1) Rotate,
#					(Walk mode 2) Walk/Rotate
#	- R1			Toggle Double gait travel speed
#	- R2			Toggle Double gait travel length
#
#	[Shift Controls]
#	- Left Stick	Shift body X/Z
#	- Right Stick	Shift body Y and rotate body Y
#
#	[Rotate Controls]
#	- Left Stick	Rotate body X/Z
#	- Right Stick	Rotate body Y
#
#	[Single leg Controls]
#	- select		Switch legs
#	- Left Stick	Move Leg X/Z (relative)
#	- Right Stick	Move Leg Y (absolute)
#	- R2			Hold/release leg position
#
#	[GP Player Controls]
#	- select		Switch Sequences
#	- R2			Start Sequence
#
#====================================================================
from wiringpi import *
import sys

LSBFIRST = 0
MSBFIRST = 1

#[CONSTANTS]
WalkMode			= 0
TranslateMode		= 1
RotateMode			= 2
SingleLegMode		= 3
GPPlayerMode		= 4
#--------------------------------------------------------------------
#[PS2 Controller Constants]
PS2DAT 				= 21		#PS2 Controller DAT (Brown)
PS2CMD 				= 19		#PS2 Controller CMD (Orange)
PS2SEL 				= 24		#PS2 Controller SEL (Blue)
PS2CLK 				= 23		#PS2 Controller CLK (White)
PadMode 			= 0x79
#--------------------------------------------------------------------
#[Ps2 Controller Variables]
DualShock 			= [0] * 7
LastButton 			= [0] * 2
DS2Mode 			= 0
PS2Index			= 0
BodyYOffset 		= 0
BodyYShift			= 0
ControlMode			= 0
DoubleHeightOn		= 0
DoubleTravelOn		= 0
WalkMethod			= 0
#--------------------------------------------------------------------
#[InitController] Initialize the PS2 controller
def InitController():

    global DS2Mode
    global BodyYOffset
    global BodyYShift

    # Set command pin to output
    pinMode(PS2CMD, OUTPUT)
    # Set data pin to input
    pinMode(PS2DAT, INPUT)
    pullUpDnControl(PS2DAT, PUD_UP)
    # Set attention pin to output
    pinMode(PS2SEL, OUTPUT)
    # Set clock pin to output
    pinMode(PS2CLK, OUTPUT)
    print("Pins setup")

    # Set command pin and clock pin high, ready to initialize a transfer.
    ##digitalWrite(PS2CMD, 1)
    digitalWrite(PS2SEL, 1)     #high PS2CLK
    LastButton[0] = 255
    LastButton[1] = 255
    BodyYOffset = 0
    BodyYShift = 0

    digitalWrite(PS2SEL, 0)     #low PS2SEL
    shiftOut(PS2CMD,PS2CLK,LSBFIRST,0x01)
    DS2Mode = shiftIn(PS2DAT,PS2CLK,MSBFIRST)
    digitalWrite(PS2SEL, 1)     #high PS2SEL
    delayMicroseconds(1000)     #pause 1

    if DS2Mode <> PadMode:
        digitalWrite(PS2SEL, 0)  # low PS2SEL
        shiftoutBytes(PS2CMD, PS2CLK, LSBFIRST, [0x01,0x43,0x00,0x01,0x00]) #shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$1\8,$43\8,$0\8,$1\8,$0\8] #CONFIG_MODE_ENTER
        digitalWrite(PS2SEL, 1)  # high PS2SEL
        delayMicroseconds(1000)  # pause 1

        digitalWrite(PS2SEL, 0)  # low PS2SEL
        shiftoutBytes(PS2CMD, PS2CLK, LSBFIRST, [0x01,0x44,0x00,0x01,0x03,0x00,0x00,0x00,0x00]) #shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$01\8,$44\8,$00\8,$01\8,$03\8,$00\8,$00\8,$00\8,$00\8] #SET_MODE_AND_LOCK
        digitalWrite(PS2SEL, 1)  # high PS2SEL
        delayMicroseconds(1000)  # pause 1

        digitalWrite(PS2SEL, 0)  # low PS2SEL
        shiftoutBytes(PS2CMD, PS2CLK, LSBFIRST, [0x01,0x4F,0x00,0xFF,0xFF,0x03,0x00,0x00,0x00]) #shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$01\8,$4F\8,$00\8,$FF\8,$FF\8,$03\8,$00\8,$00\8,$00\8] #SET_DS2_NATIVE_MODE
        digitalWrite(PS2SEL, 1)  # high PS2SEL
        delayMicroseconds(1000)  # pause 1

        digitalWrite(PS2SEL, 0)  # low PS2SEL
        shiftoutBytes(PS2CMD, PS2CLK, LSBFIRST, [0x01,0x43,0x00,0x00,0x5A,0x5A,0x5A,0x5A,0x5A]) #shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$01\8,$43\8,$00\8,$00\8,$5A\8,$5A\8,$5A\8,$5A\8,$5A\8] #CONFIG_MODE_EXIT_DS2_NATIVE
        digitalWrite(PS2SEL, 1)  # high PS2SEL
        delayMicroseconds(1000)  # pause 1

        digitalWrite(PS2SEL, 0)  # low PS2SEL
        shiftoutBytes(PS2CMD, PS2CLK, LSBFIRST, [0x01,0x43,0x00,0x00,0x00,0x00,0x00,0x00,0x00]) #shiftout PS2CMD,PS2CLK,FASTLSBPRE,[$01\8,$43\8,$00\8,$00\8,$00\8,$00\8,$00\8,$00\8,$00\8] #CONFIG_MODE_EXIT
        digitalWrite(PS2SEL, 1)  # high PS2SEL
        delayMicroseconds(100*1000)  # pause 100

        #sound([(100,4000), (100,4500), (100,5000)])

        #goto InitController #Check if the remote is initialized correctly

    return

def shiftoutBytes(dataPin, clkPin, byteOrder, data):
    for byte in data:
        shiftOut(dataPin, clkPin, byteOrder, byte)
    return

#--------------------------------------------------------------------
if wiringPiSetupGpio() == -1:
    print ("Unable to start wiringPi: %s\n" % strerror(errno))
    sys.exit(-1)

PS2CMD = physPinToGpio(PS2CMD)
PS2SEL = physPinToGpio(PS2SEL)
PS2CLK = physPinToGpio(PS2CLK)
PS2DAT = physPinToGpio(PS2DAT)
print("_commandPin=%d, _dataPin=%d, _clkPin=%d, _attnPin=%d" % (PS2CMD, PS2DAT, PS2CLK, PS2SEL))

attempts = 0
while DS2Mode <> PadMode and attempts < 20:
    InitController()
    print("DS2Mode=0x%x" % DS2Mode)
    attempts = attempts + 1
