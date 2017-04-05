from Phoenix import SLHold
from IkRoutines import LegPosX, LegPosY, LegPosZ, cInitPosX, cInitPosY, cInitPosZ
from Gait import cLR, cLF, cLM, cRF, cRM, cRR

# [Single Leg Control]
SelectedLeg = None
Prev_SelectedLeg = None
SLLegX = None
SLLegY = None
SLLegZ = None
AllDown = None


# --------------------------------------------------------------------
# Single leg control. Make sure no leg is selected
def InitSingleLeg():
    global SelectedLeg, Prev_SelectedLeg
    SelectedLeg = 255  # No Leg selected
    Prev_SelectedLeg = 255
    return


# --------------------------------------------------------------------
# [SINGLE LEG CONTROL]
def SingleLegControl():
    global Prev_SelectedLeg, AllDown

    # Check if all legs are down
    AllDown = LegPosY[cRF] == cInitPosY[cRF] and LegPosY[cRM] == cInitPosY[cRM] \
        and LegPosY[cRR] == cInitPosY[cRR] and LegPosY[cLR] == cInitPosY[cLR] \
        and LegPosY[cLM] == cInitPosY[cLM] and LegPosY[cLF] == cInitPosY[cLF]

    if 0 <= SelectedLeg <= 5:
        if SelectedLeg != Prev_SelectedLeg:

            if AllDown:  # Lift leg a bit when it got selected
                LegPosY[SelectedLeg] = cInitPosY[SelectedLeg] - 20

                # Store current status
                Prev_SelectedLeg = SelectedLeg

            else:  # Return prev leg back to the init position
                LegPosX[Prev_SelectedLeg] = cInitPosX[Prev_SelectedLeg]
                LegPosY[Prev_SelectedLeg] = cInitPosY[Prev_SelectedLeg]
                LegPosZ[Prev_SelectedLeg] = cInitPosZ[Prev_SelectedLeg]

        elif not SLHold:
            LegPosY[SelectedLeg] = LegPosY[SelectedLeg] + SLLegY
            LegPosX[SelectedLeg] = cInitPosX[SelectedLeg] + SLLegX
            LegPosZ[SelectedLeg] = cInitPosZ[SelectedLeg] + SLLegZ

    else:  # All legs to init position
        if not AllDown:
            for legIndex in range(0, 6):
                LegPosX[legIndex] = cInitPosX[legIndex]
                LegPosY[legIndex] = cInitPosY[legIndex]
                LegPosZ[legIndex] = cInitPosZ[legIndex]

        if Prev_SelectedLeg != 255:
            Prev_SelectedLeg = 255

    return
