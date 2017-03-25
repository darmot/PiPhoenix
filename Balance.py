from IkRoutines import *

# --------------------------------------------------------------------
# [BalCalcOneLeg]
BalLegNr = None


def BalCalcOneLeg(PosX, PosZ, PosY, BalLegNr):
    global TotalTransX, TotalTransY, TotalTransZ, TotalYBal, TotalZBal, TotalXBal

    # Calculating totals from center of the body to the feet
    TotalZ = cOffsetZ[BalLegNr]+PosZ
    TotalX = cOffsetX[BalLegNr]+PosX
    TotalY = 150 + PosY     # using the value 150 to lower the centerpoint of rotation #BodyPosY +
    TotalTransY = TotalTransY + PosY
    TotalTransZ = TotalTransZ + TotalZ
    TotalTransX = TotalTransX + TotalX

    GetAtan2(TotalX, TotalZ)
    TotalYBal =  TotalYBal + (Atan4*180) / 31415

    GetAtan2(TotalX, TotalY)
    TotalZBal = TotalZBal + ((Atan4*180) / 31415) -90 # Rotate balance circle 90 deg

    GetAtan2(TotalZ, TotalY)
    TotalXBal = TotalXBal + ((Atan4*180) / 31415) - 90 #Rotate balance circle 90 deg

    return


# --------------------------------------------------------------------
# [BalanceBody]
def BalanceBody():
    global TotalTransX, TotalTransY, TotalTransZ, TotalYBal, TotalXBal, TotalZBal

    TotalTransZ = TotalTransZ/6
    TotalTransX = TotalTransX/6
    TotalTransY = TotalTransY/6

    if TotalYBal > 0:		# Rotate balance circle by +/- 180 deg
        TotalYBal = TotalYBal - 180
    else:
        TotalYBal = TotalYBal + 180

    if TotalZBal < -180:    # Compensate for extreme balance positions that causes owerflow
        TotalZBal = TotalZBal + 360

    if TotalXBal < -180:    # Compensate for extreme balance positions that causes owerflow
        TotalXBal = TotalXBal + 360

    # Balance rotation
    TotalYBal = -TotalYBal/6
    TotalXBal = -TotalXBal/6
    TotalZBal = TotalZBal/6

    return


# --------------------------------------------------------------------
# [CalcBalance]
def CalcBalance():
    global TotalTransX, TotalTransY, TotalTransZ, TotalXBal, TotalYBal, TotalZBal

    TotalTransX = 0     # reset values used for calculation of balance
    TotalTransZ = 0
    TotalTransY = 0
    TotalXBal = 0
    TotalYBal = 0
    TotalZBal = 0
    if BalanceMode > 0:
        for LegIndex in range(0, 3):     # balance calculations for all Right legs
            BalCalcOneLeg(-LegPosX[LegIndex]+GaitPosX[LegIndex],
                          LegPosZ[LegIndex]+GaitPosZ[LegIndex],
                          [LegPosY[LegIndex]-cInitPosY[LegIndex]]+GaitPosY[LegIndex],
                          LegIndex)

        for LegIndex in range(3, 6):     # balance calculations for all Left legs
            BalCalcOneLeg(LegPosX[LegIndex]+GaitPosX[LegIndex],
                          LegPosZ[LegIndex]+GaitPosZ[LegIndex],
                          [LegPosY[LegIndex]-cInitPosY[LegIndex]]+GaitPosY[LegIndex],
                          LegIndex)

        BalanceBody()
        
    return
