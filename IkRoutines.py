from Config_Ch3r import *
from Trig import GetSinCos, GetBoogTan, TOFLOAT, TOINT
import math
import logging

log = logging.getLogger(__name__)

# Default leg angle
cCoxaAngle1 = [cRRCoxaAngle1, cRMCoxaAngle1, cRFCoxaAngle1, cLRCoxaAngle1, cLMCoxaAngle1, cLFCoxaAngle1]

# Body Offsets (distance between the center of the body and the center of the coxa)
cOffsetX = [cRROffsetX, cRMOffsetX, cRFOffsetX, cLROffsetX, cLMOffsetX, cLFOffsetX]
cOffsetZ = [cRROffsetZ, cRMOffsetZ, cRFOffsetZ, cLROffsetZ, cLMOffsetZ, cLFOffsetZ]

# Start positions for the leg
cInitPosX = [cRRInitPosX, cRMInitPosX, cRFInitPosX, cLRInitPosX, cLMInitPosX, cLFInitPosX]
cInitPosY = [cRRInitPosY, cRMInitPosY, cRFInitPosY, cLRInitPosY, cLMInitPosY, cLFInitPosY]
cInitPosZ = [cRRInitPosZ, cRMInitPosZ, cRFInitPosZ, cLRInitPosZ, cLMInitPosZ, cLFInitPosZ]

# Body Inverse Kinematics
BodyRotX = 0  # Global Input pitch of the body
BodyRotY = 0  # Global Input rotation of the body
BodyRotZ = 0  # Global Input roll of the body

# Gait
GaitPosX = [0] * 6  # Array containing Relative X position corresponding to the Gait
GaitPosY = [0] * 6  # Array containing Relative Y position corresponding to the Gait
GaitPosZ = [0] * 6  # Array containing Relative Z position corresponding to the Gait
GaitRotY = [0] * 6  # Array containing Relative Y rotation corresponding to the Gait

# Body position
BodyPosX = 0  # Global Input for the position of the body
BodyPosY = 0
BodyPosZ = 0

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
TotalY = None  # Total Y distance between the center of the body and the feet


# --------------------------------------------------------------------
# [BODY INVERSE KINEMATICS]
# BodyRotX         - Global Input pitch of the body
# BodyRotY         - Global Input rotation of the body
# BodyRotZ         - Global Input roll of the body
# RotationY        - Input for rotation of a single feet for the gait
# PosX             - Input position of the feet X
# PosY             - Input position of the feet Y
# PosZ             - Input position of the feet Z
# SinB             - Sin buffer for BodyRotX
# CosB             - Cos buffer for BodyRotX
# SinG             - Sin buffer for BodyRotZ
# CosG             - Cos buffer for BodyRotZ
# BodyIKPosX       - Output Position X of feet with Rotation
# BodyIKPosY       - Output Position Y of feet with Rotation
# BodyIKPosZ       - Output Position Z of feet with Rotation
def BodyIK(PosX, PosZ, PosY, TotalYBal, TotalZBal, TotalXBal, RotationY, BodyIKLeg):

    log.debug("BodyIK: PosX=%s, PosZ=%s, PosY=%s" % (PosX, PosZ, PosY))
    log.debug("BodyIK: TotalYBal=%s, TotalZBal=%s, TotalXBal=%s" % (TotalYBal, TotalZBal, TotalXBal))   
    log.debug("BodyIK: RotationY=%s, BodyIKLeg=%s" % (RotationY, BodyIKLeg)) 
    
    # Calculating totals from center of the body to the feet
    TotalZ = cOffsetZ[BodyIKLeg] + PosZ  # Total Z distance between the center of the body and the feet
    TotalX = cOffsetX[BodyIKLeg] + PosX  # Total X distance between the center of the body and the feet
    # PosY are equal to a "TotalY"

    # Successive global rotation matrix:
    # Math shorts for rotation: Alfa (A) = Xrotate, Beta (B) = Zrotate, Gamma (G) = Yrotate
    # Sinus Alfa = sinA, cosinus Alfa = cosA. and so on...

    # First calculate sinus and cosinus for each rotation:
    (SinG, CosG) = GetSinCos(TOFLOAT(BodyRotX + TotalXBal))
    (SinB, CosB) = GetSinCos(TOFLOAT(BodyRotZ + TotalZBal))
    (SinA, CosA) = GetSinCos(TOFLOAT(BodyRotY + RotationY + TotalYBal))

    # Calcualtion of rotation matrix:
    # BodyIKPosX = TotalX - (TotalX*CosA*CosB - TotalZ*CosB*SinA + PosY*SinB)
    # BodyIKPosZ = TotalZ - (TotalX*CosG*SinA + TotalX*CosA*SinB*SinG + TotalZ*CosA*CosG - TotalZ*SinA*SinB*SinG
    #                                                                                    - PosY*CosB*SinG)
    # BodyIKPosY = PosY   - (TotalX*SinA*SinG - TotalX*CosA*CosG*SinB + TotalZ*CosA*SinG + TotalZ*CosG*SinA*SinB
    #                                                                                    + PosY*CosB*CosG)
    BodyIKPosX = TotalX - TOINT(TOFLOAT(TotalX)*CosA*CosB - TOFLOAT(TotalZ)*CosB*SinA + TOFLOAT(PosY)*SinB)
    BodyIKPosZ = TotalZ - TOINT(TOFLOAT(TotalX)*CosG*SinA + TOFLOAT(TotalX)*CosA*SinB*SinG + TOFLOAT(TotalZ)*CosA*CosG - TOFLOAT(TotalZ)*SinA*SinB*SinG - TOFLOAT(PosY)*CosB*SinG)
    BodyIKPosY = PosY - TOINT(TOFLOAT(TotalX)*SinA*SinG - TOFLOAT(TotalX)*CosA*CosG*SinB + TOFLOAT(TotalZ)*CosA*SinG + TOFLOAT(TotalZ)*CosG*SinA*SinB + TOFLOAT(PosY)*CosB*CosG)

    log.debug("BodyIK: BodyIKPosX=%s, BodyIKPosY=%s, BodyIKPosZ=%s" % (BodyIKPosX, BodyIKPosY, BodyIKPosZ)) 
    return BodyIKPosX, BodyIKPosY, BodyIKPosZ


# --------------------------------------------------------------------
# [LEG INVERSE KINEMATICS] Calculates the angles of the coxa, femur and tibia for the given position of the feet
# IKFeetPosX			- Input position of the Feet X
# IKFeetPosY			- Input position of the Feet Y
# IKFeetPosZ			- Input Position of the Feet Z
# IKSolution			- Output true IF the solution is possible
# IKSolutionWarning 	- Output true IF the solution is NEARLY possible
# IKSolutionError	    - Output true IF the solution is NOT possible
# FemurAngle1	   	    - Output Angle of Femur in degrees
# TibiaAngle1  	 	    - Output Angle of Tibia in degrees
# CoxaAngle1			- Output Angle of Coxa in degrees
def LegIK(IKFeetPosX, IKFeetPosY, IKFeetPosZ, defaultCoxaAngle, IKSolution, IKSolutionWarning, IKSolutionError):

    log.debug("LegIK: IKFeetPosX=%s, IKFeetPosY=%s, IKFeetPosZ=%s" % (IKFeetPosX, IKFeetPosY, IKFeetPosZ))
    log.debug("LegIK: defaultCoxaAngle=%s" % defaultCoxaAngle)
    
    # Length between the Coxa and Feet
    IKFeetPosXZ = TOINT(math.sqrt(TOFLOAT((IKFeetPosX*IKFeetPosX)+(IKFeetPosZ*IKFeetPosZ))))

    # IKSW - Length between shoulder and wrist
    IKSW = math.sqrt(TOFLOAT(((IKFeetPosXZ-cCoxaLength)*(IKFeetPosXZ-cCoxaLength))+(IKFeetPosY*IKFeetPosY)))

    # IKA1 - Angle between SW line and the ground in rad
    IKA1 = GetBoogTan(IKFeetPosXZ-cCoxaLength, IKFeetPosY)

    # IKA2 - Angle of the line S>W with respect to the femur in radians
    Temp1 = (((cFemurLength * cFemurLength) - (cTibiaLength * cTibiaLength)) + (IKSW * IKSW))
    Temp2 = ((2 * cFemurLength) * IKSW)
    # Angle of the line S>W with respect to the femur in radians, decimals = 4
    IKA2 = math.acos(TOFLOAT(Temp1) / TOFLOAT(Temp2))

    # IKFemurAngle
    FemurAngle = (TOINT(((IKA1 + IKA2) * 180.0) / 3.141592)*-1)+90

    # IKTibiaAngle
    Temp1 = (((cFemurLength*cFemurLength) + (cTibiaLength*cTibiaLength)) - (IKSW * IKSW))
    Temp2 = (2*cFemurLength*cTibiaLength)
    TibiaAngle = (90-TOINT((math.acos(TOFLOAT(Temp1) / TOFLOAT(Temp2)) * 180.0) / 3.141592)) * -1

    # IKCoxaAngle
    BoogTan = GetBoogTan(IKFeetPosZ, IKFeetPosX)
    CoxaAngle = TOINT((BoogTan*180.0) / 3.141592)

    # Set the Solution quality    
    if (IKSW < TOFLOAT(cFemurLength+cTibiaLength-30)):
        IKSolution = 1
    else:
        if (IKSW < TOFLOAT(cFemurLength+cTibiaLength)):
            IKSolutionWarning = 1
        else:
            IKSolutionError = 1    
        #ENDIF
    #ENDIF        

    log.debug("LegIK: IKSolution=%s, IKSolutionWarning=%s, IKSolutionError=%s" % (IKSolution, IKSolutionWarning, IKSolutionError))
    log.debug("LegIK: CoxaAngle=%s, FemurAngle=%s, TibiaAngle=%s" % (CoxaAngle, FemurAngle, TibiaAngle))
    return IKSolution, IKSolutionWarning, IKSolutionError, CoxaAngle, FemurAngle, TibiaAngle

# --------------------------------------------------------------------
# [CALC INVERSE KINEMATIC] Calculates inverse kinematic
def CalcIK(TotalTransX, TotalTransY, TotalTransZ, TotalYBal, TotalZBal, TotalXBal):

    # Reset IKsolution indicators
    IKSolution = 0
    IKSolutionWarning = 0
    IKSolutionError = 0

    log.debug("CalcIK: LegPosX=[%s]" % ", ".join(map(lambda x: str(x), LegPosX)))
    log.debug("CalcIK: LegPosY=[%s]" % ", ".join(map(lambda x: str(x), LegPosY)))
    log.debug("CalcIK: LegPosZ=[%s]" % ", ".join(map(lambda x: str(x), LegPosZ)))
    log.debug("CalcIK: BodyPos(XYZ): %s, %s, %s" % (BodyPosX, BodyPosY, BodyPosZ))
    log.debug("CalcIK: TotalTrans(XYZ): %s, %s, %s" % (TotalTransX, TotalTransY, TotalTransZ))
    log.debug("CalcIK: GaitPosX=[%s]" % ", ".join(map(lambda x: str(x), GaitPosX)))
    log.debug("CalcIK: GaitPosY=[%s]" % ", ".join(map(lambda x: str(x), GaitPosY)))
    log.debug("CalcIK: GaitPosZ=[%s]" % ", ".join(map(lambda x: str(x), GaitPosZ)))
    
    # Do IK for all Right legs
    for LegIndex in range(3):
        log.debug("-----")
        log.debug("CalcIK: LegIndex=%d" % LegIndex)
        (BodyIKPosX, BodyIKPosY, BodyIKPosZ) = \
            BodyIK(-LegPosX[LegIndex] + BodyPosX + GaitPosX[LegIndex] - TotalTransX,
                   LegPosZ[LegIndex] + BodyPosZ + GaitPosZ[LegIndex] - TotalTransZ,
                   LegPosY[LegIndex] + BodyPosY + GaitPosY[LegIndex] - TotalTransY,
                   TotalYBal, TotalZBal, TotalXBal,
                   GaitRotY[LegIndex], LegIndex)
        (IKSolution, IKSolutionWarning, IKSolutionError,
         CoxaAngle1[LegIndex], FemurAngle1[LegIndex], TibiaAngle1[LegIndex]) = \
            LegIK(LegPosX[LegIndex] - BodyPosX + BodyIKPosX - GaitPosX[LegIndex] + TotalTransX,
                  LegPosY[LegIndex] + BodyPosY - BodyIKPosY + GaitPosY[LegIndex] - TotalTransY,
                  LegPosZ[LegIndex] + BodyPosZ - BodyIKPosZ + GaitPosZ[LegIndex] - TotalTransZ,
                  cCoxaAngle1[LegIndex], IKSolution, IKSolutionWarning, IKSolutionError)

    # Do IK for all Left legs
    for LegIndex in range(3, 6):
        log.debug("-----")
        log.debug("CalcIK: LegIndex=%d" % LegIndex)
        (BodyIKPosX, BodyIKPosY, BodyIKPosZ) = \
            BodyIK(LegPosX[LegIndex] - BodyPosX + GaitPosX[LegIndex] - TotalTransX,
                   LegPosZ[LegIndex] + BodyPosZ + GaitPosZ[LegIndex] - TotalTransZ,
                   LegPosY[LegIndex] + BodyPosY + GaitPosY[LegIndex] - TotalTransY,
                   TotalYBal, TotalZBal, TotalXBal,
                   GaitRotY[LegIndex], LegIndex)
        (IKSolution, IKSolutionWarning, IKSolutionError,
         CoxaAngle1[LegIndex], FemurAngle1[LegIndex], TibiaAngle1[LegIndex]) = \
            LegIK(LegPosX[LegIndex] + BodyPosX - BodyIKPosX + GaitPosX[LegIndex] - TotalTransX,
                  LegPosY[LegIndex] + BodyPosY - BodyIKPosY + GaitPosY[LegIndex] - TotalTransY,
                  LegPosZ[LegIndex] + BodyPosZ - BodyIKPosZ + GaitPosZ[LegIndex] - TotalTransZ,
                  cCoxaAngle1[LegIndex], IKSolution, IKSolutionWarning, IKSolutionError)

    # Write IK errors to leds
    LedC = IKSolutionWarning
    LedA = IKSolutionError

    log.debug("CalcIK: CoxaAngle1=[%s]" % ", ".join(map(lambda x: str(x), CoxaAngle1)))
    log.debug("CalcIK: FemurAngle1=[%s]" % ", ".join(map(lambda x: str(x), FemurAngle1)))
    log.debug("CalcIK: TibiaAngle1=[%s]" % ", ".join(map(lambda x: str(x), TibiaAngle1)))

    return CoxaAngle1, FemurAngle1, TibiaAngle1


# --------------------------------------------------------------------
# [INIT INVERSE KINEMATICS] Sets body position and rotation to 0
def InitIK():
    global BodyPosX, BodyPosY, BodyPosZ, BodyRotX, BodyRotY, BodyRotZ, BalanceMode
    # Body Positions
    BodyPosX = 0
    BodyPosY = 0
    BodyPosZ = 0

    # Body Rotations
    BodyRotX = 0
    BodyRotY = 0
    BodyRotZ = 0
    BalanceMode = 0
    log.debug("InitIK: Body-positions set to 0")
    return
