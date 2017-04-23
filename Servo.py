# Build tables for Leg configuration like I/O and MIN/MAX values to easy access values using a FOR loop
# Constants are still defined as single values in the cfg file to make it easy to read/configure

import time
import serial
from Config_Ch3r import cRRCoxaPin, cRMCoxaPin, cRFCoxaPin, cLRCoxaPin, cLMCoxaPin, cLFCoxaPin, \
    cRRFemurPin, cRMFemurPin, cRFFemurPin, cLRFemurPin, cLMFemurPin, cLFFemurPin, \
    cRRTibiaPin, cRMTibiaPin, cRFTibiaPin, cLRTibiaPin, cLMTibiaPin, cLFTibiaPin, \
    cRRCoxaMin1, cRMCoxaMin1, cRFCoxaMin1, cLRCoxaMin1, cLMCoxaMin1, cLFCoxaMin1, \
    cRRCoxaMax1, cRMCoxaMax1, cRFCoxaMax1, cLRCoxaMax1, cLMCoxaMax1, cLFCoxaMax1, \
    cRRFemurMin1, cRMFemurMin1, cRFFemurMin1, cLRFemurMin1, cLMFemurMin1, cLFFemurMin1, \
    cRRFemurMax1, cRMFemurMax1, cRFFemurMax1, cLRFemurMax1, cLMFemurMax1, cLFFemurMax1, \
    cRRTibiaMin1, cRMTibiaMin1, cRFTibiaMin1, cLRTibiaMin1, cLMTibiaMin1, cLFTibiaMin1, \
    cRRTibiaMax1, cRMTibiaMax1, cRFTibiaMax1, cLRTibiaMax1, cLMTibiaMax1, cLFTibiaMax1, \
    cSSC_BAUD
from Gait import cLR, cLF, cLM, cRF, cRM, cRR, \
    TravelLengthX, TravelLengthZ, TravelRotationY, \
    NomGaitSpeed, cTravelDeadZone
from IkRoutines import GaitPosX, GaitPosY, GaitPosZ, GaitRotY, BalanceMode, \
    CoxaAngle1, FemurAngle1, TibiaAngle1, \
    LegPosX, LegPosY, LegPosZ, \
    cInitPosX, cInitPosY, cInitPosZ
from SingleLeg import AllDown

# SSC Pin numbers
cCoxaPin = [cRRCoxaPin, cRMCoxaPin, cRFCoxaPin, cLRCoxaPin, cLMCoxaPin, cLFCoxaPin]
cFemurPin = [cRRFemurPin, cRMFemurPin, cRFFemurPin, cLRFemurPin, cLMFemurPin, cLFFemurPin]
cTibiaPin = [cRRTibiaPin, cRMTibiaPin, cRFTibiaPin, cLRTibiaPin, cLMTibiaPin, cLFTibiaPin]

# Min / Max values
cCoxaMin1 = [cRRCoxaMin1, cRMCoxaMin1, cRFCoxaMin1, cLRCoxaMin1, cLMCoxaMin1, cLFCoxaMin1]
cCoxaMax1 = [cRRCoxaMax1, cRMCoxaMax1, cRFCoxaMax1, cLRCoxaMax1, cLMCoxaMax1, cLFCoxaMax1]
cFemurMin1 = [cRRFemurMin1, cRMFemurMin1, cRFFemurMin1, cLRFemurMin1, cLMFemurMin1, cLFFemurMin1]
cFemurMax1 = [cRRFemurMax1, cRMFemurMax1, cRFFemurMax1, cLRFemurMax1, cLMFemurMax1, cLFFemurMax1]
cTibiaMin1 = [cRRTibiaMin1, cRMTibiaMin1, cRFTibiaMin1, cLRTibiaMin1, cLMTibiaMin1, cLFTibiaMin1]
cTibiaMax1 = [cRRTibiaMax1, cRMTibiaMax1, cRFTibiaMax1, cLRTibiaMax1, cLMTibiaMax1, cLFTibiaMax1]

ser = None

# --------------------------------------------------------------------
# [TIMING]
CycleTime           = None  # Total Cycle time (in milliseconds)
lTimerStart         = None  # Start time of the calculation cycles (in milliseconds)
lTimerEnd           = None  # End time of the calculation cycles (in milliseconds)
PrevSSCTime         = None  # Previous time for the servo updates
SSCTime             = None  # Time for servo updates

# --------------------------------------------------------------------
# [Simple function to get the current time in milliseconds ]
def GetCurrentTime():
    lCurrentTime = int(time.time()*1000)
    return lCurrentTime                        # switched back to basic


# --------------------------------------------------------------------
# Startet den Timer
def StartTimer():
    global lTimerStart
    lTimerStart = GetCurrentTime()
    return


# --------------------------------------------------------------------
# [CHECK ANGLES] Checks the mechanical limits of the servos
def CheckAngles():
    for LegIndex in range(6):
        CoxaAngle1[LegIndex] = max(min(CoxaAngle1[LegIndex], cCoxaMin1[LegIndex]), cCoxaMax1[LegIndex])
        FemurAngle1[LegIndex] = max(min(FemurAngle1[LegIndex], cFemurMin1[LegIndex]), cFemurMax1[LegIndex])
        TibiaAngle1[LegIndex] = max(min(TibiaAngle1[LegIndex], cTibiaMin1[LegIndex]), cTibiaMax1[LegIndex])
    return


# --------------------------------------------------------------------
# [SERVO DRIVER MAIN] Updates the positions of the servos
def ServoDriverMain(Eyes, HexOn, Prev_HexOn, InputTimeDelay, SpeedControl):
    global lTimerEnd, PrevSSCTime, SSCTime, CycleTime

    # print("ServoDriveMain: HexOn=%d, Prev_HexOn=%d\n" % (HexOn, Prev_HexOn))

    if HexOn:
        if HexOn and Prev_HexOn == 0:
            sound([(60, 4000), (80, 4500), (100, 5000)])
            Eyes = 1

        # Set SSC time
        if abs(TravelLengthX) > cTravelDeadZone \
                or abs(TravelLengthZ) > cTravelDeadZone \
                or abs(TravelRotationY * 2) > cTravelDeadZone:
            SSCTime = NomGaitSpeed + (InputTimeDelay * 2) + SpeedControl

            # Add aditional delay when Balance mode is on
            if BalanceMode:
                SSCTime += 100

        else:  # Movement speed excl. Walking
            SSCTime = 200 + SpeedControl

            # Sync BAP with SSC while walking to ensure the prev is completed before sending the next one
        if (GaitPosX[cRF] or GaitPosX[cRM] or GaitPosX[cRR] or GaitPosX[cLF] or GaitPosX[cLM] or GaitPosX[cLR] or
                GaitPosY[cRF] or GaitPosY[cRM] or GaitPosY[cRR] or GaitPosY[cLF] or GaitPosY[cLM] or GaitPosY[cLR] or
                GaitPosZ[cRF] or GaitPosZ[cRM] or GaitPosZ[cRR] or GaitPosZ[cLF] or GaitPosZ[cLM] or GaitPosZ[cLR] or
                GaitRotY[cRF] or GaitRotY[cRM] or GaitRotY[cRR] or GaitRotY[cLF] or GaitRotY[cLM] or GaitRotY[cLR]):
            # Get endtime and calculate wait time
            lTimerEnd = GetCurrentTime()
            CycleTime = lTimerEnd - lTimerStart

            # Wait for previous commands to be completed while walking
            # Min 1 ensures that there always is a value in the  pause command
            pause(min((PrevSSCTime - CycleTime - 45), 1))

        PrevSSCTime = ServoDriver(SSCTime)

    else:

        # Turn the bot off
        if Prev_HexOn or not AllDown:
            SSCTime = 600
            PrevSSCTime = ServoDriver(SSCTime)
            sound([(100, 5000), (80, 4500), (60, 4000)])
            pause(600)
        else:
            FreeServos()
            Eyes = 0

    return Eyes


# --------------------------------------------------------------------
# [SERVO DRIVER] Updates the positions of the servos
def ServoDriver(SSCTime):

    # Update Right Legs
    for LegIndex in range(3):
        serout(["#", cCoxaPin[LegIndex], "P", (-CoxaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(["#", cFemurPin[LegIndex], "P", (-FemurAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(["#", cTibiaPin[LegIndex], "P", (-TibiaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])

    # Update Left Legs
    for LegIndex in range(3, 6):
        serout(["#", cCoxaPin[LegIndex], "P", (CoxaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(["#", cFemurPin[LegIndex], "P", (FemurAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(["#", cTibiaPin[LegIndex], "P", (TibiaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])

    # Send <CR>
    serout(["T", SSCTime, "\r"])

    PrevSSCTime = SSCTime
    return PrevSSCTime


# --------------------------------------------------------------------
# [FREE SERVOS] Frees all the servos
def FreeServos():
    for LegIndex in range(32):
        serout(["#", LegIndex, "P0"])

    serout(["T200\r"])
    return


# --------------------------------------------------------------------
# [GET SSC VERSION] Checks SSC version number if it ends with "GP"
# enable the GP player if it does
def GetSSCVersion():
    pause(10)
    GPEnable = 0
    print "vor serout ver"
    serout(["ver\r"])
    print "nach serout ver"
    s = readline()
    if s.endswith("GP\r"):
        GPEnable = 1
    else:
        sound([(40, 5000), (40, 5000)])
        pass

    # Index = 0
    #    while 1:
    #        serin(cSSC_IN, cSSC_BAUD, 1000, timeout, [GPVerData[Index]])
    #        Index = (Index+1)%3 # shift last 3 chars in data
    #
    #
    #    timeout:
    #    if (GPVerData[0] + GPVerData[1] + GPVerData[2]) == 164 : # Check if the last 3 chars are G(71) P(80) cr(13)
    #        GPEnable = 1
    #    else:
    #        sound(P9, [(40,5000),(40,5000)])

    pause(10)
    return GPEnable


# --------------------------------------------------------------------
# [INIT SERVOS] Sets start positions for each leg
def InitServos():
    global ser, SSCTime

    for LegIndex in range(6):
        LegPosX[LegIndex] = cInitPosX[LegIndex]  # Set start positions for each leg
        LegPosY[LegIndex] = cInitPosY[LegIndex]
        LegPosZ[LegIndex] = cInitPosZ[LegIndex]

    # SSC
    SSCTime = 150

    ser = serial.Serial('/dev/ttyUSB0', cSSC_BAUD)
    print "XXX"
    GPEnable = GetSSCVersion()

    return GPEnable


# --------------------------------------------------------------------
# [GP PLAYER]
GPStatSeq = 0
GPStatFromStep = 0
GPStatToStep = 0
GPStatTime = 0


def GPPlayer(GPStart, GPSeq):
    # Start sequence
    if GPStart == 1:
        serout(["PL0SQ", GPSeq, "ONCE\r"])  # Start sequence

        # Wait for GPPlayer to complete sequence
        while GPStatSeq != 255 or GPStatFromStep != 0 or GPStatToStep != 0 or GPStatTime != 0:
            serout(["QPL0\r"])
            serin([GPStatSeq, GPStatFromStep, GPStatToStep, GPStatTime])

        GPStart = 0
    return GPStart


# --------------------------------------------------------------------
def pause(milliseconds):
    time.sleep(milliseconds / 1000)
    return


# --------------------------------------------------------------------
def serout(outputData):
    print outputData
    x = reduce(lambda accu, d: accu + str(d), outputData)
    print x
    print "serout: x=%s" % x
    ser.write(x)
    return


# --------------------------------------------------------------------
def serin(inputData):
    ser.readinto(inputData)
    return


# --------------------------------------------------------------------
def readline():
    print "readline 1"
    x = ser.read_until(serial.CR)
    print "readline 2"
    return x


# --------------------------------------------------------------------
# list of tuples of duration in millisecvons and note in Hz (frequency)
def sound(listOfDurationAndNotes):
    print listOfDurationAndNotes
    return


