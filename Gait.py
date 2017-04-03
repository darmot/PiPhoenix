from IkRoutines import GaitPosX, GaitPosY, GaitPosZ, GaitRotY

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
TravelLengthX   = None  # Current Travel length X
TravelLengthZ   = None  # Current Travel length Z
TravelRotationY = None  # Current Travel Rotation Y

TLDivFactor     = None  # Number of steps that a leg is on the floor while walking
NrLiftedPos     = None  # Number of positions that a single leg is lifted (1-3)
HalfLiftHeigth  = None  # If TRUE the outer positions of the ligted legs will be half height

GaitInMotion    = None  # Temp to check if the gait is in motion
StepsInGait     = None  # Number of steps in gait
LastLeg         = None  # TRUE when the current leg is the last leg of the sequence
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

    return


# --------------------------------------------------------------------
# [GAIT Sequence]
def GaitSeq():
    global LastLeg
    # Calculate Gait sequence
    LastLeg = 0
    for LegIndex in range(0, 6):    # for all legs
        if LegIndex == 5:           # last leg
            LastLeg = 1

        Gait(LegIndex)
    return


# --------------------------------------------------------------------
# [GAIT]
def Gait(GaitCurrentLegNr):
    global GaitInMotion, TravelLengthX, TravelLengthZ, TravelRotationY, GaitStep

    # Check IF the Gait is in motion
    GaitInMotion = ((abs(TravelLengthX) > cTravelDeadZone)
                    or (abs(TravelLengthZ) > cTravelDeadZone) or (abs(TravelRotationY) > cTravelDeadZone))

    # Clear values under the cTravelDeadZone
    if GaitInMotion == 0:
        TravelLengthX = 0
        TravelLengthZ = 0
        TravelRotationY = 0

    # Leg middle up position
    # Gait in motion														  Gait NOT in motion, return to home position
    if ((GaitInMotion and (NrLiftedPos == 1 or NrLiftedPos == 3) and GaitStep == GaitLegNr[GaitCurrentLegNr])
        or (not GaitInMotion and GaitStep == GaitLegNr[GaitCurrentLegNr] and ((abs(GaitPosX[GaitCurrentLegNr]) > 2)
            and (abs(GaitPosZ[GaitCurrentLegNr]) > 2) or (abs(GaitRotY[GaitCurrentLegNr]) > 2)))):   # Up
        GaitPosX[GaitCurrentLegNr] = 0
        GaitPosY[GaitCurrentLegNr] = -LegLiftHeight
        GaitPosZ[GaitCurrentLegNr] = 0
        GaitRotY[GaitCurrentLegNr] = 0

    else:
        # Optional Half heigth Rear
        if (((NrLiftedPos == 2 and GaitStep == GaitLegNr[GaitCurrentLegNr])
                or (NrLiftedPos == 3
                and (GaitStep == GaitLegNr[GaitCurrentLegNr]-1
                     or GaitStep == GaitLegNr[GaitCurrentLegNr]+(StepsInGait-1))))
                and GaitInMotion):
            GaitPosX[GaitCurrentLegNr] = -TravelLengthX/2
            GaitPosY[GaitCurrentLegNr] = -LegLiftHeight/(HalfLiftHeigth+1)
            GaitPosZ[GaitCurrentLegNr] = -TravelLengthZ/2
            GaitRotY[GaitCurrentLegNr] = -TravelRotationY/2

        else:
            # Optional half heigth front
            if ((NrLiftedPos >= 2)
                    and (GaitStep == GaitLegNr[GaitCurrentLegNr] + 1
                         or GaitStep == GaitLegNr[GaitCurrentLegNr]-(StepsInGait-1))
                    and GaitInMotion):
                GaitPosX[GaitCurrentLegNr] = TravelLengthX/2
                GaitPosY[GaitCurrentLegNr] = -LegLiftHeight/(HalfLiftHeigth+1)
                GaitPosZ[GaitCurrentLegNr] = TravelLengthZ/2
                GaitRotY[GaitCurrentLegNr] = TravelRotationY/2

            else:
                # Leg front down position
                if (GaitStep == GaitLegNr[GaitCurrentLegNr] + NrLiftedPos
                        or GaitStep == GaitLegNr[GaitCurrentLegNr] - (StepsInGait-NrLiftedPos)) \
                        and GaitPosY(GaitCurrentLegNr)<0:
                    GaitPosX[GaitCurrentLegNr] = TravelLengthX/2
                    GaitPosZ[GaitCurrentLegNr] = TravelLengthZ/2
                    GaitRotY[GaitCurrentLegNr] = TravelRotationY/2
                    GaitPosY[GaitCurrentLegNr] = 0	# Only move leg down at once if terrain adaption is turned off

                # Move body forward
                else:
                    GaitPosX[GaitCurrentLegNr] = GaitPosX[GaitCurrentLegNr] - (TravelLengthX/TLDivFactor)
                    GaitPosY[GaitCurrentLegNr] = 0
                    GaitPosZ[GaitCurrentLegNr] = GaitPosZ[GaitCurrentLegNr] - (TravelLengthZ/TLDivFactor)
                    GaitRotY[GaitCurrentLegNr] = GaitRotY[GaitCurrentLegNr] - (TravelRotationY/TLDivFactor)

    # Advance to the next step
    if LastLeg:     # The last leg in this step
        GaitStep = GaitStep+1
        if GaitStep > StepsInGait:
            GaitStep = 1

    return
