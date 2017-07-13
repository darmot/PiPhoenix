from IkRoutines import GaitPosX, GaitPosY, GaitPosZ, GaitRotY

import logging

log = logging.getLogger(__name__)

# [CONSTANTS]
cRR = 0
cRM = 1
cRF = 2
cLR = 3
cLM = 4
cLF = 5

# [REMOTE]
cTravelDeadZone = 4     # The deadzone for the analog input from the remote

# --------------------------------------------------------------------
# [gait]
GaitType        = None  # Gait type
NomGaitSpeed    = None  # Nominal speed of the gait

LegLiftHeight   = None 	# Current Travel height

TLDivFactor     = None  # Number of steps that a leg is on the floor while walking
NrLiftedPos     = None  # Number of positions that a single leg is lifted (1-3)
HalfLiftHeigth  = None  # If TRUE the outer positions of the ligted legs will be half height

GaitInMotion    = None  # Temp to check if the gait is in motion
StepsInGait     = None  # Number of steps in gait
GaitStep        = None 	# Actual Gait step

GaitLegNr       = [None] * 6  # Init position of the leg

GaitLegNrIn     = None  # Input Number of the leg


# --------------------------------------------------------------------
def InitGait():
    global GaitType, LegLiftHeight, GaitStep

    GaitType = 0
    LegLiftHeight = 50
    GaitStep = 1
    # fall through to GaitSelect
    GaitSelect()
    log.debug("InitGait: GaitType=%d, legLiftHeight=%d, GaitStep=%d, NomGaitSpeed=%d" % (GaitType, LegLiftHeight, GaitStep, NomGaitSpeed))
    return


# --------------------------------------------------------------------
def GaitSelect():
    global NrLiftedPos, HalfLiftHeigth, TLDivFactor, StepsInGait, NomGaitSpeed

    # Gait selector
    if GaitType == 0:     # Ripple Gait 6 steps
        GaitLegNr[cLR] = 1
        GaitLegNr[cRF] = 2
        GaitLegNr[cLM] = 3
        GaitLegNr[cRR] = 4
        GaitLegNr[cLF] = 5
        GaitLegNr[cRM] = 6

        NrLiftedPos = 1
        HalfLiftHeigth = 0
        TLDivFactor = 4
        StepsInGait = 6
        NomGaitSpeed = 100

    if GaitType == 1:       # Ripple Gait 12 steps
        GaitLegNr[cLR] = 1
        GaitLegNr[cRF] = 3
        GaitLegNr[cLM] = 5
        GaitLegNr[cRR] = 7
        GaitLegNr[cLF] = 9
        GaitLegNr[cRM] = 11

        NrLiftedPos = 3
        HalfLiftHeigth = 0  # 1
        TLDivFactor = 8
        StepsInGait = 12
        NomGaitSpeed = 85

    if GaitType == 2:     # Quadripple 9 steps
        GaitLegNr[cLR] = 1
        GaitLegNr[cRF] = 2
        GaitLegNr[cLM] = 4
        GaitLegNr[cRR] = 5
        GaitLegNr[cLF] = 7
        GaitLegNr[cRM] = 8

        NrLiftedPos = 2
        HalfLiftHeigth = 0
        TLDivFactor = 6
        StepsInGait = 9
        NomGaitSpeed = 100

    if GaitType == 3:     # Tripod 4 steps
        GaitLegNr[cLR] = 3
        GaitLegNr[cRF] = 1
        GaitLegNr[cLM] = 1
        GaitLegNr[cRR] = 1
        GaitLegNr[cLF] = 3
        GaitLegNr[cRM] = 3

        NrLiftedPos = 1
        HalfLiftHeigth = 0
        TLDivFactor = 2
        StepsInGait = 4
        NomGaitSpeed = 150

    if GaitType == 4:     # Tripod 6 steps
        GaitLegNr[cLR] = 4
        GaitLegNr[cRF] = 1
        GaitLegNr[cLM] = 1
        GaitLegNr[cRR] = 1
        GaitLegNr[cLF] = 4
        GaitLegNr[cRM] = 4

        NrLiftedPos = 2
        HalfLiftHeigth = 0
        TLDivFactor = 4
        StepsInGait = 6
        NomGaitSpeed = 100

    if GaitType == 5:     # Tripod 8 steps
        GaitLegNr[cLR] = 5
        GaitLegNr[cRF] = 1
        GaitLegNr[cLM] = 1
        GaitLegNr[cRR] = 1
        GaitLegNr[cLF] = 5
        GaitLegNr[cRM] = 5

        NrLiftedPos = 3
        HalfLiftHeigth = 1
        TLDivFactor = 4
        StepsInGait = 8
        NomGaitSpeed = 85

    if GaitType == 6:     # Wave 12 steps
        GaitLegNr[cLR] = 1
        GaitLegNr[cRF] = 11
        GaitLegNr[cLM] = 3

        GaitLegNr[cRR] = 7
        GaitLegNr[cLF] = 5
        GaitLegNr[cRM] = 9

        NrLiftedPos = 1
        HalfLiftHeigth = 0
        TLDivFactor = 10
        StepsInGait = 12
        NomGaitSpeed = 85

    if GaitType == 7:     # Wave 18 steps
        GaitLegNr[cLR] = 4
        GaitLegNr[cRF] = 1
        GaitLegNr[cLM] = 7

        GaitLegNr[cRR] = 13
        GaitLegNr[cLF] = 10
        GaitLegNr[cRM] = 16

        NrLiftedPos = 2
        HalfLiftHeigth = 0
        TLDivFactor = 16
        StepsInGait = 18
        NomGaitSpeed = 85

    log.debug("GaitSelect: GaitType=%d" % GaitType)
    return


# --------------------------------------------------------------------
# [GAIT Sequence]
def GaitSeq(TravelLengthX, TravelLengthZ, TravelRotationY):

    log.debug("GaitSeq: TravelLengthX=%d, TravelLengthZ=%d, TravelRotationY=%d" % (TravelLengthX, TravelLengthZ, TravelRotationY))
    # Calculate Gait sequence
    LastLeg = 0  # TRUE when the current leg is the last leg of the sequence
    for LegIndex in range(0, 6):    # for all legs
        if LegIndex == 5:           # last leg
            LastLeg = 1

        (TravelLengthX, TravelLengthZ, TravelRotationY) = Gait(LegIndex, LastLeg, TravelLengthX, TravelLengthZ, TravelRotationY)
    
    log.debug("GaitSeq: TravelLengthX=%d, TravelLengthZ=%d, TravelRotationY=%d" % (TravelLengthX, TravelLengthZ, TravelRotationY))
    return TravelLengthX, TravelLengthZ, TravelRotationY


# --------------------------------------------------------------------
# [GAIT]
def Gait(LegNr, LastLeg, TravelLengthX, TravelLengthZ, TravelRotationY):
    global GaitInMotion, GaitStep

    log.debug("Gait: TravelLengthX=%d, TravelLengthZ=%d, TravelRotationY=%d" % (TravelLengthX, TravelLengthZ, TravelRotationY))
    # Check IF the Gait is in motion
    GaitInMotion = ((abs(TravelLengthX) > cTravelDeadZone)
                    or (abs(TravelLengthZ) > cTravelDeadZone)
                    or (abs(TravelRotationY) > cTravelDeadZone))
    log.debug("Gait: GaitInMotion=%d" % GaitInMotion)

    # Clear values under the cTravelDeadZone
    if GaitInMotion == 0:
        TravelLengthX = 0
        TravelLengthZ = 0
        TravelRotationY = 0

    log.debug("Gait: LegNr=%d, LastLeg=%d, TravelLengthX=%d, TravelLengthZ=%d, TravelRotationY=%d" % (LegNr, LastLeg, TravelLengthX, TravelLengthZ, TravelRotationY))

    # Leg middle up position
    # Gait in motion														  Gait NOT in motion, return to home position
    if ((GaitInMotion and GaitStep == GaitLegNr[LegNr] and (NrLiftedPos == 1 or NrLiftedPos == 3))
        or (not GaitInMotion and GaitStep == GaitLegNr[LegNr]
            and ((abs(GaitPosX[LegNr]) > 2) or (abs(GaitPosZ[LegNr]) > 2) or (abs(GaitRotY[LegNr]) > 2)))):   # Up
        log.debug("Gait: Case 1")
        GaitPosX[LegNr] = 0
        GaitPosY[LegNr] = -LegLiftHeight
        GaitPosZ[LegNr] = 0
        GaitRotY[LegNr] = 0

    else:
        # Optional Half heigth Rear
        if (((NrLiftedPos == 2 and GaitStep == GaitLegNr[LegNr])
            or (NrLiftedPos == 3 and (GaitStep == GaitLegNr[LegNr] - 1 or GaitStep == GaitLegNr[LegNr] + (StepsInGait - 1))))
                and GaitInMotion):
            log.debug("Gait: Case 2")
            GaitPosX[LegNr] = -TravelLengthX/2
            GaitPosY[LegNr] = -LegLiftHeight/(HalfLiftHeigth+1)
            GaitPosZ[LegNr] = -TravelLengthZ/2
            GaitRotY[LegNr] = -TravelRotationY/2

        else:
            # Optional half heigth front
            if ((NrLiftedPos >= 2) and (GaitStep == GaitLegNr[LegNr] + 1 or GaitStep == GaitLegNr[LegNr]-(StepsInGait-1))
                    and GaitInMotion):
                log.debug("Gait: Case 3")
                GaitPosX[LegNr] = TravelLengthX/2
                GaitPosY[LegNr] = -LegLiftHeight/(HalfLiftHeigth+1)
                GaitPosZ[LegNr] = TravelLengthZ/2
                GaitRotY[LegNr] = TravelRotationY/2

            else:
                # Leg front down position
                if ((GaitStep == GaitLegNr[LegNr] + NrLiftedPos or GaitStep == GaitLegNr[LegNr] - (StepsInGait-NrLiftedPos)) 
                    and GaitPosY[LegNr] < 0):
                    log.debug("Gait: Case 4")
                    GaitPosX[LegNr] = TravelLengthX/2
                    GaitPosZ[LegNr] = TravelLengthZ/2
                    GaitRotY[LegNr] = TravelRotationY/2
                    GaitPosY[LegNr] = 0  # Only move leg down at once if terrain adaption is turned off

                # Move body forward
                else:
                    log.debug("Gait: Case 5")
                    GaitPosX[LegNr] = GaitPosX[LegNr] - (TravelLengthX/TLDivFactor)
                    GaitPosY[LegNr] = 0
                    GaitPosZ[LegNr] = GaitPosZ[LegNr] - (TravelLengthZ/TLDivFactor)
                    GaitRotY[LegNr] = GaitRotY[LegNr] - (TravelRotationY/TLDivFactor)

    # Advance to the next step
    if LastLeg:     # The last leg in this step
        GaitStep = GaitStep+1
        log.debug("Gait: LastLeg=True, GaitStep=%d" % GaitStep)
        if GaitStep > StepsInGait:
            GaitStep = 1
            log.debug("Gait: GaiStep>StepsInGait, GaitStep=%d" % GaitStep)

    return TravelLengthX, TravelLengthZ, TravelRotationY
