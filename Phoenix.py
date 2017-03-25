# Project Lynxmotion Phoenix
# Description: Phoenix software
# Software version: V2.0
# Date: 29-10-2009
# Programmer: Jeroen Janssen (aka Xan)
# 
# Hardware setup: ABB2 with ATOM 28 Pro, SSC32 V2
# 
# NEW IN V2.0
# 	- Moved to fixed point calculations
# 	- Inverted BodyRotX and BodyRotZ direction
# 	- Added deadzone for switching gaits
# 	- Added GP Player
# 	- SSC version check to enable/disable GP player
# 	- Controls changed, Check contol file for more information
# 	- Added separate files for control and configuration functions
# 	- Solved bug at turn-off sequence
# 	- Solved bug about legs beeing lift at small travelvalues in 4 steps tripod gait
# 	- Solved bug about body translate results in rotate when balance is on (Kåre)
# 	- Sequence for wave gait changed (Kåre)
# 	- Improved ATan2 function for IK (Kåre)
# 	- Added option to turn on/off eyes (leds)
# 	- Moving legs to init position improved
# 	- Using Indexed values for legs
# 	- Added single leg control
# 
# KNOWN BUGS:
# 	- None at the moment # )
# 
# Project file order:
# 	1. config_ch3r_v20.bas
# 	2. phoenix_V2x.bas
# 	3. phoenix_Control_ps2.bas
# ====================================================================
import time
import Gait
import Servo
import SingleLeg
import Balance
import IkRoutines
import PhoenixControlPs2

# --------------------------------------------------------------------
# [CONSTANTS]
BUTTON_DOWN = 0
BUTTON_UP   = 1

# --------------------------------------------------------------------
# [POSITIONS SINGLE LEG CONTROL]
SLHold      = None		 	# Single leg control mode

# --------------------------------------------------------------------
# [INPUTS]
butA    = None
butB    = None
butC    = None

prev_butA = None
prev_butB = None
prev_butC = None
# --------------------------------------------------------------------
# [GP PLAYER]
GPStart     = None		  # Start the GP Player
GPSeq       = None		  # Number of the sequence
GPVerData   = [None] * 3  # Received data to check the SSC Version
GPEnable    = None        # Enables the GP player when the SSC version ends with "GP<cr>"
# --------------------------------------------------------------------
# [OUTPUTS]
LedA = None  # Red
LedB = None  # Green
LedC = None  # Orange
Eyes = None  # Eyes output
# --------------------------------------------------------------------
# [VARIABLES]
Index = None		# Index universal used

# --------------------------------------------------------------------
# [TIMING]
lTimerStart         = None  # Start time of the calculation cycles (in milliseconds)
lTimerEnd           = None 	# End time of the calculation cycles (in milliseconds)
CycleTime           = None  # Total Cycle time (in milliseconds)

SSCTime             = None  # Time for servo updates
PrevSSCTime         = None  # Previous time for the servo updates

InputTimeDelay      = None  # Delay that depends on the input to get the "sneaking" effect
SpeedControl        = None  # Adjustible Delay
# --------------------------------------------------------------------
# [GLOABAL]
HexOn               = None  # Switch to turn on Phoenix
Prev_HexOn          = None  # Previous loop state


# ====================================================================
# [INIT]
def Init():
    global LedA, LedB, LedC, Eyes, SSCTime, HexOn

    Servo.GetSSCVersion()

    # Turning off all the leds
    LedA = 0
    LedB = 0
    LedC = 0
    Eyes = 0
  
    Servo.InitServos()  		# Tars Init Positions
    SingleLeg.InitSingleLeg()
    IkRoutines.InitIK()
    Gait.InitGait()

    # Initialize Controller
    PhoenixControlPs2.InitController()

    # SSC
    SSCTime = 150
    HexOn = 0
    return


# ====================================================================
# [MAIN]
def MainLoop():
    global lTimerStart, Prev_HexOn

    # main:
    while 1:
        # time.sleep(1)  # pause 1000

        # Start time
        lTimerStart = GetCurrentTime()
  
        PhoenixControlPs2.ControlInput()		# Read input
  
        # ReadButtons()		# I/O used by the remote
        WriteOutputs()		# Write Outputs

        # GP Player
        if GPEnable:
            Servo.GPPlayer()

        SingleLeg.SingleLegControl() 	# Single leg control
        Gait.GaitSeq()  			# Gait
        Balance.CalcBalance()  		# Balance calculations
        IkRoutines.CalcIK()  			# calculate inverse kinematic
        Servo.CheckAngles()  		# Check mechanical limits
        Servo.ServoDriverMain()  	# Drive Servos
    
        # Store previous HexOn State
        if HexOn:
            Prev_HexOn = 1
        else:
            Prev_HexOn = 0

        # goto main

    # dead:
    # goto dead
    return


# ====================================================================
# [ReadButtons] Reading input buttons from the ABB
def ReadButtons():
    global prev_butA, prev_butB, prev_butC
    # input P4
    # input P5
    # input P6

    prev_butA = butA
    prev_butB = butB
    prev_butC = butC

    # butA = IN4
    # butB = IN5
    # butC = IN6
    return


# --------------------------------------------------------------------
# [WriteOutputs] Updates the state of the leds
def WriteOutputs():
    #   IF ledA = 1 THEN
    # 	low p4
    #   ENDIF
    #   IF ledB = 1 THEN
    # 	low p5
    #   ENDIF
    #   IF ledC = 1 THEN
    # 	low p6
    #   ENDIF
    if Eyes == 0:
        # wiringpi.digitalWrite(cEyesPin, 0)
        pass
    else:
        # wiringpi.digitalWrite(cEyesPin, 1)
        pass

    return


# --------------------------------------------------------------------
# [Simple function to get the current time in milliseconds ]
def GetCurrentTime():
    lCurrentTime = int(time.time()*1000)
    return lCurrentTime						# switched back to basic


# --------------------------------------------------------------------
# [Entry point]
Init()
MainLoop()
