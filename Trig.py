import math
import logging

log = logging.getLogger(__name__)


# --------------------------------------------------------------------
# [GETSINCOS] Get the sinus and cosinus from the angle +/- multiple circles
# AngleDeg 	- Input Angle in degrees
# Sin  	    - Output Sinus of the given Angle
# Cos  		- Output Cosinus of the given Angle
def GetSinCos(AngleDeg):

    # Get the absolute value of the Angle in Degrees
    if AngleDeg < 0.0:
        ABSAngleDeg = AngleDeg * (-1.0)
    else:
        ABSAngleDeg = AngleDeg

    # Shift rotation to a full circle of 360 deg -> AngleDeg // 360
    if AngleDeg < 0.0:   # Negative values
        AngleDeg = 360.0 - (ABSAngleDeg - TOFLOAT(360*(TOINT(ABSAngleDeg / 360.0))))
    else:				# Positive values
        AngleDeg = ABSAngleDeg - TOFLOAT(360 * (TOINT(ABSAngleDeg / 360.0)))

    if AngleDeg < 180.0:                   # Angle between 0 and 180
        # Subtract 90 to shift range
        AngleDeg = AngleDeg -90.0
        # Convert degree to radials
        AngleRad = (AngleDeg*3.141592)/180.0

        SinA = math.cos(AngleRad)      # Sin o to 180 deg = cos(Angle Rad - 90deg)
        CosA = -math.sin(AngleRad)     # Cos 0 to 180 deg = -sin(Angle Rad - 90deg)

    else:                                   # Angle between 180 and 360
        # Subtract 270 to shift range
        AngleDeg = AngleDeg -270.0
        # Convert degree to radials
        AngleRad = (AngleDeg*3.141592)/180.0

        SinA = -math.cos(AngleRad)     # Sin 180 to 360 deg = -cos(Angle Rad - 270deg)
        CosA = math.sin(AngleRad)      # Cos 180 to 360 deg = sin(Angle Rad - 270deg)
    

    return SinA, CosA

# --------------------------------------------------------------------
# [BOOGTAN2] Gets the Inverse Tangus from X/Y with the where Y can be zero or negative
# BoogTanX         - Input X
# BoogTanY         - Input Y
# BoogTan          - Output BOOGTANs(X/Y)
def GetBoogTan(BoogTanX, BoogTanY):
    
    if (BoogTanX == 0):    # X=0 -> 0 or PI
        if (BoogTanY >= 0):
            BoogTan = 0.0
        else:
            BoogTan = 3.141592
        #ENDIF
    else:

        if (BoogTanY == 0):    # Y=0 -> +/- Pi/2
            if (BoogTanX > 0):
                BoogTan = 3.141592 / 2.0
            else:
                BoogTan = -3.141592 / 2.0
            #ENDIF
        else:

            if (BoogTanY > 0):    # BOOGTAN(X/Y)
                BoogTan = math.atan(TOFLOAT(BoogTanX) / TOFLOAT(BoogTanY))
            else:    
                if (BoogTanX > 0):    # BOOGTAN(X/Y) + PI    
                    BoogTan = math.atan(TOFLOAT(BoogTanX) / TOFLOAT(BoogTanY)) + 3.141592
                else:                    # BOOGTAN(X/Y) - PI    
                    BoogTan = math.atan(TOFLOAT(BoogTanX) / TOFLOAT(BoogTanY)) - 3.141592
                #ENDIF
            #ENDIF
        #ENDIF
    #ENDIF
    return BoogTan

def TOFLOAT(val):
    return float(val)

def TOINT(val):
    return int(val)
