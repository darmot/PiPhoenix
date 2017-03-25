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
wTimerWOverflowCnt  = None  # used in WTimer overflow. Will keep a 16 bit overflow so we have a 32 bit timer
lCurrentTime        = None
lTimerStart         = None  # Start time of the calculation cycles
lTimerEnd           = None 	# End time of the calculation cycles
CycleTime           = None  # Total Cycle time

SSCTime             = None  # Time for servo updates
PrevSSCTime         = None  # Previous time for the servo updates

InputTimeDelay      = None  # Delay that depends on the input to get the "sneaking" effect
SpeedControl        = None  # Adjustible Delay
# --------------------------------------------------------------------
# [GLOABAL]
HexOn               = None	# Switch to turn on Phoenix
Prev_HexOn          = None	# Previous loop state

# ====================================================================
# [TIMER INTERRUPT INIT]
### TODO ONASMINTERRUPT TIMERWINT, Handle_TIMERW
# ====================================================================
# [INIT]

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

# Timer
### TODO WTIMERTICSPERMS con 2000#  we have 16 clocks per ms and we are incrementing every 8 so divide again by 2
TCRW = 0x30 			# clears TCNT and sets the timer to inc clock cycle / 8 
TMRW = 0x80 			# starts the timer counting 
wTimerWOverflowCnt = 0 
### TODO enable TIMERWINT_OVF 	# enable timer interrupt
### TODO enable					# enables all interrupts

# Initialize Controller
PhoenixControlPs2.InitController()

# SSC
SSCTime = 150
HexOn = 0
# ====================================================================
# [MAIN]	
# main:
while 1:
    # pause 1000

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
# [Handle TimerW interrupt]
# BEGINASMSUB
# HANDLE_TIMERW
# ASM {
#  push.w   r1							#  save away register we will use
#  bclr #7,@TSRW:8						#  clear the overflow bit in the Timer status word
#  mov.w @WTIMERWOVERFLOWCNT:16,r1		#  We will increment the word that is the highword for a clock timer
#  inc.w #1,r1
#  mov.w r1, @WTIMERWOVERFLOWCNT:16
#  pop.w  r1								#  restore our registers
#  rte									#  and return
# }
# return
# ENDASMSUB
# -------------------------------------------------------------------------------------

# [Simple function to get the current time and verify that no overflow happened]

def GetCurrentTime():
    # ASM {
    #  nop      #  probably not needed, but to make sure we are in assembly mode
    #  mov.w  @WTIMERWOVERFLOWCNT:16, e1
    #  mov.w  @TCNT:16, r1
    #  mov.w  @WTIMERWOVERFLOWCNT:16, r2
    #  cmp.w  r2,e1							#  make sure no overflow happened
    #  beq           _GCT_RETURN:8			#  no overflow, so return it
    #
    #  mov.w  @WTIMERWOVERFLOWCNT:16, e1
    #  mov.w  @TCNT:16, r1
    #
    # _GCT_RETURN:
    #  mov.l  er1, @LCURRENTTIME:16
    # }
    return lCurrentTime						# switched back to basic
# --------------------------------------------------------------------