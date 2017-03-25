# Build tables for Leg configuration like I/O and MIN/MAX values to easy access values using a FOR loop
# Constants are still defined as single values in the cfg file to make it easy to read/configure

import time
from Config_Ch3r import *

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


# --------------------------------------------------------------------
# [CHECK ANGLES] Checks the mechanical limits of the servos
def CheckAngles(CoxaAngle1, FemurAngle1, TibiaAngle1):
    for LegIndex in range(6):
        CoxaAngle1[LegIndex] = max(min(CoxaAngle1[LegIndex], cCoxaMin1[LegIndex]), cCoxaMax1[LegIndex])
        FemurAngle1[LegIndex] = max(min(FemurAngle1[LegIndex], cFemurMin1[LegIndex]), cFemurMax1[LegIndex])
        TibiaAngle1[LegIndex] = max(min(TibiaAngle1[LegIndex], cTibiaMin1[LegIndex]), cTibiaMax1[LegIndex])
    return


# --------------------------------------------------------------------
# [SERVO DRIVER MAIN] Updates the positions of the servos
def ServoDriverMain(HexOn, Prev_HexOn, TravelLengthX, TravelLengthZ, TravelRotationY, NomGaitSpeed, InputTimeDelay,
                    SpeedControl, cTravelDeadZone, BalanceMode, GaitPosX, GaitPosY, GaitPosZ, GaitRotY, cRF, cRM,
                    cRR, cLF, cLM, cLR, PrevSSCTime, AllDown, lTimerStart):
    # serout S_OUT, i38400, ["ServoDriveMain: HexOn=",dec HexOn,", Prev_HexOn=",dec Prev_HexOn,13]

    if HexOn:
        if HexOn and Prev_HexOn == 0:
            # Sound P9,[60\4000,80\4500,100\5000]
            Eyes = 1

        # Set SSC time
        if abs(TravelLengthX) > cTravelDeadZone or abs(TravelLengthZ) > cTravelDeadZone or abs(
                        TravelRotationY * 2) > cTravelDeadZone:
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
            pause(min((PrevSSCTime - CycleTime - 45),
                      1))  # Min 1 ensures that there always is a value in the pause command

        ServoDriver()

    else:

        # Turn the bot off
        if Prev_HexOn or not AllDown:
            SSCTime = 600
            ServoDriver()
            # Sound P9,[100\5000,80\4500,60\4000]
            pause(600)
        else:
            FreeServos()
            Eyes = 0

    return Eyes, SSCTime


# --------------------------------------------------------------------
# [SERVO DRIVER] Updates the positions of the servos
def ServoDriver(cSSC_OUT, cSSC_BAUD, CoxaAngle1, FemurAngle1, TibiaAngle1, SSCTime):

    # Update Right Legs
    for LegIndex in range(3):
        serout(cSSC_OUT, cSSC_BAUD, ["#", cCoxaPin[LegIndex], "P", (-CoxaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(cSSC_OUT, cSSC_BAUD, ["#", cFemurPin[LegIndex], "P", (-FemurAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(cSSC_OUT, cSSC_BAUD, ["#", cTibiaPin[LegIndex], "P", (-TibiaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])

    # Update Left Legs
    for LegIndex in range(3, 6):
        serout(cSSC_OUT, cSSC_BAUD, ["#", cCoxaPin[LegIndex], "P", (CoxaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(cSSC_OUT, cSSC_BAUD, ["#", cFemurPin[LegIndex], "P", (FemurAngle1[LegIndex] + 900) * 1000 / 1059 + 650])
        serout(cSSC_OUT, cSSC_BAUD, ["#", cTibiaPin[LegIndex], "P", (TibiaAngle1[LegIndex] + 900) * 1000 / 1059 + 650])

    # Send <CR>
    serout(cSSC_OUT, cSSC_BAUD, ["T", SSCTime, 13])

    PrevSSCTime = SSCTime
    return PrevSSCTime


# --------------------------------------------------------------------
# [FREE SERVOS] Frees all the servos
def FreeServos(cSSC_OUT, cSSC_BAUD):
    for LegIndex in range(32):
        serout(cSSC_OUT, cSSC_BAUD, ["#", LegIndex, "P0"])

    serout(cSSC_OUT, cSSC_BAUD, ["T200", 13])
    return


# --------------------------------------------------------------------
# [GET SSC VERSION] Checks SSC version number if it ends with "GP"
# enable the GP player if it does
def GetSSCVersion(cSSC_OUT, cSSC_IN, cSSC_BAUD):
    pause(10)
    GPEnable = 0
    # Index = 0
    serout(cSSC_OUT, cSSC_BAUD, ["ver", 13])
    readline(cSSC_IN, cSSC_BAUD)
    if str.endswith("GP\r"):
        GPEnable = 1
    else:
        # sound(P9, [(40, 5000), (40, 5000)])
        pass

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
def InitServos(LegPosX, LegPosY, LegPosZ, cInitPosX, cInitPosY, cInitPosZ):
    for LegIndex in range(6):
        LegPosX[LegIndex] = cInitPosX[LegIndex]  # Set start positions for each leg
        LegPosY[LegIndex] = cInitPosY[LegIndex]
        LegPosZ[LegIndex] = cInitPosZ[LegIndex]
    return


# --------------------------------------------------------------------
# [GP PLAYER]
GPStatSeq = 0
GPStatFromStep = 0
GPStatToStep = 0
GPStatTime = 0


def GPPlayer(GPStart, GPSeq, cSSC_OUT, cSSC_BAUD, cSSC_IN):
    # Start sequence
    if GPStart == 1:
        serout(cSSC_OUT, cSSC_BAUD, ["PL0SQ", GPSeq, "ONCE", 13])  # Start sequence

        # Wait for GPPlayer to complete sequence
        while GPStatSeq != 255 or GPStatFromStep != 0 or GPStatToStep != 0 or GPStatTime != 0:
            serout(cSSC_OUT, cSSC_BAUD, ["QPL0", 13])
            serin(cSSC_IN, cSSC_BAUD, [GPStatSeq, GPStatFromStep, GPStatToStep, GPStatTime])

        GPStart = 0
    return GPStart


# --------------------------------------------------------------------
def pause(milliseconds):
    time.sleep(milliseconds / 1000)
    return


# --------------------------------------------------------------------
def serout(txPin, baudMode, outputData):
    ### TODO format string and send to ssc
    return


# --------------------------------------------------------------------
def serin(rxPin, baudMode, inputData):
    return


# --------------------------------------------------------------------
def readline(rxPin, baudMode):
    return "\r";


# --------------------------------------------------------------------
# list of tuples of duration in millisecvons and note in Hz (frequency)
def sound(pin, listOfDurationAndNotes):
    return


# --------------------------------------------------------------------
# must return a 32 Bit timer
def GetCurrentTime():
    return 0
