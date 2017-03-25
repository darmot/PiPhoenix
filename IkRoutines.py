from Config_Ch3r import *
from Trig import *

# LegIndex = None  # Index used for leg Index Number

# Default leg angle
cCoxaAngle1 = [None] * 6
cRRCoxaAngle1 = cCoxaAngle1[0]
cRMCoxaAngle1 = cCoxaAngle1[1]
cRFCoxaAngle1 = cCoxaAngle1[2]
cLRCoxaAngle1 = cCoxaAngle1[3]
cLMCoxaAngle1 = cCoxaAngle1[4]
cLFCoxaAngle1 = cCoxaAngle1[5]

# Body Offsets (distance between the center of the body and the center of the coxa)
cOffsetX = [None] * 6
cRROffsetX = cOffsetX[0]
cRMOffsetX = cOffsetX[1]
cRFOffsetX = cOffsetX[2]
cLROffsetX = cOffsetX[3]
cLMOffsetX = cOffsetX[4]
cLFOffsetX = cOffsetX[5]
cOffsetZ = [None] * 6
cRROffsetZ = cOffsetZ[0]
cRMOffsetZ = cOffsetZ[1]
cRFOffsetZ = cOffsetZ[2]
cLROffsetZ = cOffsetZ[3]
cLMOffsetZ = cOffsetZ[4]
cLFOffsetZ = cOffsetZ[5]

# Start positions for the leg
cInitPosX = [None] * 6
cRRInitPosX = cInitPosX[0]
cRMInitPosX = cInitPosX[1]
cRFInitPosX = cInitPosX[2]
cLRInitPosX = cInitPosX[3]
cLMInitPosX = cInitPosX[4]
cLFInitPosX = cInitPosX[5]
cInitPosY = [None] * 6
cRRInitPosY = cInitPosY[0]
cRMInitPosY = cInitPosY[1]
cRFInitPosY = cInitPosY[2]
cLRInitPosY = cInitPosY[3]
cLMInitPosY = cInitPosY[4]
cLFInitPosY = cInitPosY[5]
cInitPosZ = [None] * 6
cRRInitPosZ = cInitPosZ[0]
cRMInitPosZ = cInitPosZ[1]
cRFInitPosZ = cInitPosZ[2]
cLRInitPosZ = cInitPosZ[3]
cLMInitPosZ = cInitPosZ[4]
cLFInitPosZ = cInitPosZ[5]

# Body Inverse Kinematics
BodyRotX = None  # Global Input pitch of the body
BodyRotY = None  # Global Input rotation of the body
BodyRotZ = None  # Global Input roll of the body
PosX = None  # Input position of the feet X
PosZ = None  # Input position of the feet Z
PosY = None  # Input position of the feet Y
RotationY = None  # Input for rotation of a single feet for the gait
sinA4 = None  # Sin buffer for BodyRotX calculations
cosA4 = None  # Cos buffer for BodyRotX calculations
sinB4 = None  # Sin buffer for BodyRotX calculations
cosB4 = None  # Cos buffer for BodyRotX calculations
sinG4 = None  # Sin buffer for BodyRotZ calculations
cosG4 = None  # Cos buffer for BodyRotZ calculations
TotalX = None  # Total X distance between the center of the body and the feet
TotalZ = None  # Total Z distance between the center of the body and the feet
BodyIKPosX = None  # Output Position X of feet with Rotation
BodyIKPosY = None  # Output Position Y of feet with Rotation
BodyIKPosZ = None  # Output Position Z of feet with Rotation

# Leg Inverse Kinematics
IKFeetPosX = None  # Input position of the Feet X
IKFeetPosY = None  # Input position of the Feet Y
IKFeetPosZ = None  # Input Position of the Feet Z
IKFeetPosXZ = None  # Diagonal direction from Input X and Z
IKSW2 = None  # Length between Shoulder and Wrist, decimals = 2
IKA14 = None  # Angle of the line S>W with respect to the ground in radians, decimals = 4
IKA24 = None  # Angle of the line S>W with respect to the femur in radians, decimals = 4
Temp1 = None
Temp2 = None
IKSolution = None  # Output true if the solution is possible
IKSolutionWarning = None  # Output true if the solution is NEARLY possible
IKSolutionError = None  # Output true if the solution is NOT possible

# Gait
GaitPosX = [None] * 6  # Array containing Relative X position corresponding to the Gait
GaitPosY = [None] * 6  # Array containing Relative Y position corresponding to the Gait
GaitPosZ = [None] * 6  # Array containing Relative Z position corresponding to the Gait
GaitRotY = [None] * 6  # Array containing Relative Y rotation corresponding to the Gait

# Body position
BodyPosX = None  # Global Input for the position of the body
BodyPosY = None
BodyPosZ = None

LegPosX = [None] * 6  # Actual X Posion of the Leg
LegPosY = [None] * 6  # Actual Y Posion of the Leg
LegPosZ = [None] * 6  # Actual Z Posion of the Leg

# ====================================================================
# [ANGLES]
CoxaAngle1 = [None] * 6  # Actual Angle of the horizontal hip, decimals = 1
FemurAngle1 = [None] * 6  # Actual Angle of the vertical hip, decimals = 1
TibiaAngle1 = [None] * 6  # Actual Angle of the knee, decimals = 1

# --------------------------------------------------------------------
# [Balance]
BalanceMode = None
TotalTransX = None
TotalTransZ = None
TotalTransY = None
TotalYbal = None
TotalXBal = None
TotalZBal = None
TotalY = None  # Total Y distance between the center of the body and the feet

# --------------------------------------------------------------------
# [BODY INVERSE KINEMATICS]
# BodyRotX         - Global Input pitch of the body
# BodyRotY         - Global Input rotation of the body
# BodyRotZ         - Global Input roll of the body
# RotationY         - Input Rotation for the gait
# PosX            - Input position of the feet X
# PosZ            - Input position of the feet Z
# SinB          		- Sin buffer for BodyRotX
# CosB           	- Cos buffer for BodyRotX
# SinG          		- Sin buffer for BodyRotZ
# CosG           	- Cos buffer for BodyRotZ
# BodyIKPosX         - Output Position X of feet with Rotation
# BodyIKPosY         - Output Position Y of feet with Rotation
# BodyIKPosZ         - Output Position Z of feet with Rotation
BodyIKLeg = None


def BodyIK(PosX, PosZ, PosY, RotationY, BodyIKLeg):
    global TotalX, TotalZ
    global BodyIKPosX, BodyIKPosY, BodyIKPosZ

    # Calculating totals from center of the body to the feet
    TotalZ = cOffsetZ[BodyIKLeg] + PosZ
    TotalX = cOffsetX[BodyIKLeg] + PosX
    # PosY are equal to a "TotalY"

    # Successive global rotation matrix:
    # Math shorts for rotation: Alfa (A) = Xrotate, Beta (B) = Zrotate, Gamma (G) = Yrotate
    # Sinus Alfa = sinA, cosinus Alfa = cosA. and so on...

    # First calculate sinus and cosinus for each rotation:
    GetSinCos((BodyRotX + TotalXBal) * c1DEC)
    SinG4 = Sin4
    CosG4 = Cos4

    GetSinCos((BodyRotZ + TotalZBal) * c1DEC)
    SinB4 = Sin4
    CosB4 = Cos4

    GetSinCos((BodyRotY + RotationY + TotalYbal) * c1DEC)
    SinA4 = Sin4
    CosA4 = Cos4

    # Calcualtion of rotation matrix:
    # BodyIKPosX = TotalX - (TotalX*CosA*CosB - TotalZ*CosB*SinA + PosY*SinB)
    # BodyIKPosZ = TotalZ - (TotalX*CosG*SinA + TotalX*CosA*SinB*SinG + TotalZ*CosA*CosG - TotalZ*SinA*SinB*SinG - PosY*CosB*SinG)
    # BodyIKPosY = PosY   - (TotalX*SinA*SinG - TotalX*CosA*CosG*SinB + TotalZ*CosA*SinG + TotalZ*CosG*SinA*SinB + PosY*CosB*CosG)
    BodyIKPosX = (TotalX * c2DEC - (
        TotalX * c2DEC * CosA4 / c4DEC * CosB4 / c4DEC - TotalZ * c2DEC * CosB4 / c4DEC * SinA4 / c4DEC + PosY * c2DEC * SinB4 / c4DEC)) / c2DEC
    BodyIKPosZ = (TotalZ * c2DEC - (
        TotalX * c2DEC * CosG4 / c4DEC * SinA4 / c4DEC + TotalX * c2DEC * CosA4 / c4DEC * SinB4 / c4DEC * SinG4 / c4DEC + TotalZ * c2DEC * CosA4 / c4DEC * CosG4 / c4DEC - TotalZ * c2DEC * SinA4 / c4DEC * SinB4 / c4DEC * SinG4 / c4DEC - PosY * c2DEC * CosB4 / c4DEC * SinG4 / c4DEC)) / c2DEC
    BodyIKPosY = (PosY * c2DEC - (
        TotalX * c2DEC * SinA4 / c4DEC * SinG4 / c4DEC - TotalX * c2DEC * CosA4 / c4DEC * CosG4 / c4DEC * SinB4 / c4DEC + TotalZ * c2DEC * CosA4 / c4DEC * SinG4 / c4DEC + TotalZ * c2DEC * CosG4 / c4DEC * SinA4 / c4DEC * SinB4 / c4DEC + PosY * c2DEC * CosB4 / c4DEC * CosG4 / c4DEC)) / c2DEC

    return


# --------------------------------------------------------------------
# [LEG INVERSE KINEMATICS] Calculates the angles of the coxa, femur and tibia for the given position of the feet
# IKFeetPosX			- Input position of the Feet X
# IKFeetPosY			- Input position of the Feet Y
# IKFeetPosZ			- Input Position of the Feet Z
# IKSolution			- Output true IF the solution is possible
# IKSolutionWarning 	- Output true IF the solution is NEARLY possible
# IKSolutionError	- Output true IF the solution is NOT possible
# FemurAngle1	   	- Output Angle of Femur in degrees
# TibiaAngle1  	 	- Output Angle of Tibia in degrees
# CoxaAngle1			- Output Angle of Coxa in degrees
LegIKLegNr = None


def LegIK(IKFeetPosX, IKFeetPosY, IKFeetPosZ, LegIKLegNr):
    # Calculate IKCoxaAngle and IKFeetPosXZ
    GetAtan2(IKFeetPosX, IKFeetPosZ)
    CoxaAngle1[LegIKLegNr] = ((Atan4 * 180) / 3141) + cCoxaAngle1[LegIKLegNr]

    # Length between the Coxa and tars (foot)
    IKFeetPosXZ = XYhyp2 / c2DEC

    # Using GetAtan2 for solving IKA1 and IKSW
    # IKA14 - Angle between SW line and the ground in radians
    IKA14 = GetAtan2(IKFeetPosY, IKFeetPosXZ - cCoxaLength)
    # IKSW2 - Length between femur axis and tars
    IKSW2 = XYhyp2

    # IKA2 - Angle of the line S>W with respect to the femur in radians
    Temp1 = (((cFemurLength * cFemurLength) - (cTibiaLength * cTibiaLength)) * c4DEC + (IKSW2 * IKSW2))
    Temp2 = ((2 * cFemurLength) * c2DEC * IKSW2)
    IKA24 = GetArcCos(Temp1 / (Temp2 / c4DEC))

    # IKFemurAngle
    FemurAngle1[LegIKLegNr] = -(IKA14 + IKA24) * 180 / 3141 + 900

    # IKTibiaAngle
    Temp1 = (((cFemurLength * cFemurLength) + (cTibiaLength * cTibiaLength)) * c4DEC - (IKSW2 * IKSW2))
    Temp2 = (2 * cFemurLength * cTibiaLength)
    GetArcCos(Temp1 / Temp2)
    TibiaAngle1[LegIKLegNr] = -(900 - AngleRad4 * 180 / 3141)

    # Set the Solution quality
    if IKSW2 < (cFemurLength + cTibiaLength - 30) * c2DEC:
        IKSolution = 1
    else:
        if IKSW2 < (cFemurLength + cTibiaLength) * c2DEC:
            IKSolutionWarning = 1
        else:
            IKSolutionError = 1
    return


# --------------------------------------------------------------------
# [CALC INVERSE KINEMATIC] Calculates inverse kinematic
def CalcIK():
    # Reset IKsolution indicators
    IKSolution = 0
    IKSolutionWarning = 0
    IKSolutionError = 0

    # Do IK for all Right legs
    for LegIndex in range(3):
        BodyIK(-LegPosX[LegIndex] + BodyPosX + GaitPosX[LegIndex] - TotalTransX,
               LegPosZ[LegIndex] + BodyPosZ + GaitPosZ[LegIndex] - TotalTransZ,
               LegPosY[LegIndex] + BodyPosY + GaitPosY[LegIndex] - TotalTransY,
               GaitRotY[LegIndex], LegIndex)
        LegIK(LegPosX[LegIndex] - BodyPosX + BodyIKPosX - (GaitPosX[LegIndex] - TotalTransX),
              LegPosY[LegIndex] + BodyPosY - BodyIKPosY + GaitPosY[LegIndex] - TotalTransY,
              LegPosZ[LegIndex] + BodyPosZ - BodyIKPosZ + GaitPosZ[LegIndex] - TotalTransZ, LegIndex)

    # Do IK for all Left legs
    for LegIndex in range(3, 5):
        BodyIK(LegPosX[LegIndex] - BodyPosX + GaitPosX[LegIndex] - TotalTransX,
               LegPosZ[LegIndex] + BodyPosZ + GaitPosZ[LegIndex] - TotalTransZ,
               LegPosY[LegIndex] + BodyPosY + GaitPosY[LegIndex] - TotalTransY,
               GaitRotY[LegIndex], LegIndex)
        LegIK(LegPosX[LegIndex] + BodyPosX - BodyIKPosX + GaitPosX[LegIndex] - TotalTransX,
              LegPosY[LegIndex] + BodyPosY - BodyIKPosY + GaitPosY[LegIndex] - TotalTransY,
              LegPosZ[LegIndex] + BodyPosZ - BodyIKPosZ + GaitPosZ[LegIndex] - TotalTransZ, LegIndex)

    # Write IK errors to leds
    LedC = IKSolutionWarning
    LedA = IKSolutionError

    return


# --------------------------------------------------------------------
# [INIT INVERSE KINEMATICS] Sets body position and rotation to 0
def InitIK():
    # Body Positions
    BodyPosX = 0
    BodyPosY = 0
    BodyPosZ = 0

    # Body Rotations
    BodyRotX = 0
    BodyRotY = 0
    BodyRotZ = 0
    return
