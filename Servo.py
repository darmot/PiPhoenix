# Build tables for Leg configuration like I/O and MIN/MAX values to easy access values using a FOR loop
# Constants are still defined as single values in the cfg file to make it easy to read/configure

import logging
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
import Gait
from IkRoutines import GaitPosX, GaitPosY, GaitPosZ, GaitRotY, BalanceMode, \
    LegPosX, LegPosY, LegPosZ, \
    cInitPosX, cInitPosY, cInitPosZ
from SingleLeg import AllDown

log = logging.getLogger(__name__)

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
def CheckAngles(CoxaAngle1, FemurAngle1, TibiaAngle1):
    log.debug("CheckAngles: cCoxaMin1=[%s]" % ", ".join(map(lambda x: str(x), cCoxaMin1)))
    log.debug("CheckAngles: cCoxaMax1=[%s]" % ", ".join(map(lambda x: str(x), cCoxaMax1)))
    log.debug("CheckAngles: cFemurMin1=[%s]" % ", ".join(map(lambda x: str(x), cFemurMin1)))
    log.debug("CheckAngles: cFemurMax1=[%s]" % ", ".join(map(lambda x: str(x), cFemurMax1)))
    log.debug("CheckAngles: cTibiaMin1=[%s]" % ", ".join(map(lambda x: str(x), cTibiaMin1)))
    log.debug("CheckAngles: cTibiaMax1=[%s]" % ", ".join(map(lambda x: str(x), cTibiaMax1)))

    for LegIndex in range(6):
        CoxaAngle1[LegIndex] = min(max(CoxaAngle1[LegIndex], cCoxaMin1[LegIndex]), cCoxaMax1[LegIndex])
        FemurAngle1[LegIndex] = min(max(FemurAngle1[LegIndex], cFemurMin1[LegIndex]), cFemurMax1[LegIndex])
        TibiaAngle1[LegIndex] = min(max(TibiaAngle1[LegIndex], cTibiaMin1[LegIndex]), cTibiaMax1[LegIndex])

    log.debug("CheckAngles: CoxaAngle1=[%s]" % ", ".join(map(lambda x: str(x), CoxaAngle1)))
    log.debug("CheckAngles: FemurAngle1=[%s]" % ", ".join(map(lambda x: str(x), FemurAngle1)))
    log.debug("CheckAngles: TibiaAngle1=[%s]" % ", ".join(map(lambda x: str(x), TibiaAngle1)))
    
    return (CoxaAngle1, FemurAngle1, TibiaAngle1)


# --------------------------------------------------------------------
# [SERVO DRIVER MAIN] Updates the positions of the servos
def ServoDriverMain(Eyes, HexOn, Prev_HexOn, InputTimeDelay, SpeedControl, TravelLengthX, TravelLengthZ, TravelRotationY, CoxaAngle1, FemurAngle1, TibiaAngle1):
    global lTimerEnd, PrevSSCTime, SSCTime, CycleTime

    log.debug("ServoDriveMain: HexOn=%s, Prev_HexOn=%s\n" % (HexOn, Prev_HexOn))

    if HexOn:
        
        log.debug("ServoDriverMain: switched on")
        
        if HexOn and Prev_HexOn == 0:
            sound([(60, 4000), (80, 4500), (100, 5000)])
            Eyes = 1

        log.debug("ServoDriveMain: NomGaitSpeed=%d" % Gait.NomGaitSpeed)
        log.debug("ServoDriveMain: InputTimeDelay=%d" % InputTimeDelay)
        log.debug("ServoDriveMain: SpeedControl=%d" % SpeedControl)

        # Set SSC time
        if abs(TravelLengthX) > Gait.cTravelDeadZone \
                or abs(TravelLengthZ) > Gait.cTravelDeadZone \
                or abs(TravelRotationY * 2) > Gait.cTravelDeadZone:
            SSCTime = Gait.NomGaitSpeed + (InputTimeDelay * 2) + SpeedControl

            # Add aditional delay when Balance mode is on
            if BalanceMode:
                SSCTime += 100

        else:  # Movement speed excl. Walking
            SSCTime = 200 + SpeedControl

        # Sync BAP with SSC while walking to ensure the prev is completed before sending the next one
        if (GaitPosX[Gait.cRF] or GaitPosX[Gait.cRM] or GaitPosX[Gait.cRR] or GaitPosX[Gait.cLF] or GaitPosX[Gait.cLM] or GaitPosX[Gait.cLR] or
                GaitPosY[Gait.cRF] or GaitPosY[Gait.cRM] or GaitPosY[Gait.cRR] or GaitPosY[Gait.cLF] or GaitPosY[Gait.cLM] or GaitPosY[Gait.cLR] or
                GaitPosZ[Gait.cRF] or GaitPosZ[Gait.cRM] or GaitPosZ[Gait.cRR] or GaitPosZ[Gait.cLF] or GaitPosZ[Gait.cLM] or GaitPosZ[Gait.cLR] or
                GaitRotY[Gait.cRF] or GaitRotY[Gait.cRM] or GaitRotY[Gait.cRR] or GaitRotY[Gait.cLF] or GaitRotY[Gait.cLM] or GaitRotY[Gait.cLR]):
            # Get endtime and calculate wait time
            lTimerEnd = GetCurrentTime()
            CycleTime = lTimerEnd - lTimerStart

            log.debug("ServoDriverMain: PrevSSCTime=%d" % PrevSSCTime)
            log.debug("ServoDriverMain: CycleTime=%d" % CycleTime)
            # Wait for previous commands to be completed while walking
            # Min 1 ensures that there always is a value in the  pause command
            pause(max((PrevSSCTime - CycleTime - 45), 1))

        PrevSSCTime = ServoDriver(SSCTime, CoxaAngle1, FemurAngle1, TibiaAngle1)

    else:
        
        log.debug("ServoDriverMain: switched off")
        
        # Turn the bot off
        if Prev_HexOn or not AllDown:
            SSCTime = 600
            PrevSSCTime = ServoDriver(SSCTime, CoxaAngle1, FemurAngle1, TibiaAngle1)
            sound([(100, 5000), (80, 4500), (60, 4000)])
            pause(600)
        else:
            FreeServos()
            Eyes = 0

    return Eyes


# --------------------------------------------------------------------
# [SERVO DRIVER] Updates the positions of the servos
def ServoDriver(SSCTime, CoxaAngle1, FemurAngle1, TibiaAngle1):

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
    log.debug("FreeServos:")
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
    log.debug("Check SSC-version")
    serout(["ver\r"])
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

    ser = serial.Serial('/dev/ttyUSB0', cSSC_BAUD, timeout=5)
    GPEnable = GetSSCVersion()

    return GPEnable


# --------------------------------------------------------------------
# [GP PLAYER]
GPStatSeq = 0
GPStatFromStep = 0
GPStatToStep = 0
GPStatTime = 0


def GPPlayer(GPStart, GPSeq):
    log.debug("GPPlayer: GPStart=%d, GPSeq=%d" % (GPStart, GPSeq))
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
    log.debug("pause: milliseconds=%d" % milliseconds)
    time.sleep(milliseconds / 1000)
    return


# --------------------------------------------------------------------
def serout(outputData):
    log.debug("serout:" + str(outputData))
    x = reduce(lambda accu, d: accu + str(d), outputData)
    log.debug("serout: x=%s" % x)
    ser.write(x)
    return


# --------------------------------------------------------------------
def serin(inputData):
    ser.readinto(inputData)
    return


# --------------------------------------------------------------------
def readline():
    log.debug("readline 1")
    x = ser.read_until(serial.CR)
    log.debug("readline returned '%s'" % x)
    return x


# --------------------------------------------------------------------
# list of tuples of duration in millisecvons and note in Hz (frequency)
def sound(listOfDurationAndNotes):
    log.debug("sound: [%s]" % ', '.join(map(lambda t: "(%d, %d)" % t, listOfDurationAndNotes)))
    return


