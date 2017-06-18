import math
import logging

log = logging.getLogger(__name__)

c1DEC = 10
c2DEC = 100
c4DEC = 10000
c6DEC = 1000000

# --------------------------------------------------------------------
# [TABLES]
# ArcCosinus Table
# Table build in to 3 part to get higher accuracy near cos = 1.
# The biggest error is near cos = 1 and has a biggest value of 3*0.012098rad = 0.521 deg.
# -	Cos 0 to 0.9 is done by steps of 0.0079 rad. (1/127)
# -	Cos 0.9 to 0.99 is done by steps of 0.0008 rad (0.1/127)
# -	Cos 0.99 to 1 is done by step of 0.0002 rad (0.01/64)
# Since the tables are overlapping the full range of 127+127+64 is not necessary. Total bytes: 277
GetACos = [
    255, 254, 252, 251, 250, 249, 247, 246, 245, 243, 242, 241, 240, 238, 237, 236, 234, 233, 232, 231, 229, 228, 227, 225,
    224, 223, 221, 220, 219, 217, 216, 215, 214, 212, 211, 210, 208, 207, 206, 204, 203, 201, 200, 199, 197, 196, 195, 193,
    192, 190, 189, 188, 186, 185, 183, 182, 181, 179, 178, 176, 175, 173, 172, 170, 169, 167, 166, 164, 163, 161, 160, 158,
    157, 155, 154, 152, 150, 149, 147, 146, 144, 142, 141, 139, 137, 135, 134, 132, 130, 128, 127, 125, 123, 121, 119, 117,
    115, 113, 111, 109, 107, 105, 103, 101, 98, 96, 94, 92, 89, 87, 84, 81, 79, 76, 73, 73, 73, 72, 72, 72, 71, 71, 71, 70, 70,
    70, 70, 69, 69, 69, 68, 68, 68, 67, 67, 67, 66, 66, 66, 65, 65, 65, 64, 64, 64, 63, 63, 63, 62, 62, 62, 61, 61, 61, 60, 60, 59,
    59, 59, 58, 58, 58, 57, 57, 57, 56, 56, 55, 55, 55, 54, 54, 53, 53, 53, 52, 52, 51, 51, 51, 50, 50, 49, 49, 48, 48, 47, 47, 47,
    46, 46, 45, 45, 44, 44, 43, 43, 42, 42, 41, 41, 40, 40, 39, 39, 38, 37, 37, 36, 36, 35, 34, 34, 33, 33, 32, 31, 31, 30, 29, 28,
    28, 27, 26, 25, 24, 23, 23, 23, 23, 22, 22, 22, 22, 21, 21, 21, 21, 20, 20, 20, 19, 19, 19, 19, 18, 18, 18, 17, 17, 17, 17, 16,
    16, 16, 15, 15, 15, 14, 14, 13, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 8, 7, 6, 6, 5, 3, 0]

# Sin table 90 deg, persision 0.5 deg (180 values)
GetSin = [0, 87, 174, 261, 348, 436, 523, 610, 697, 784, 871, 958, 1045, 1132, 1218, 1305, 1391, 1478, 1564,
          1650, 1736, 1822, 1908, 1993, 2079, 2164, 2249, 2334, 2419, 2503, 2588, 2672, 2756, 2840, 2923, 3007,
          3090, 3173, 3255, 3338, 3420, 3502, 3583, 3665, 3746, 3826, 3907, 3987, 4067, 4146, 4226, 4305, 4383,
          4461, 4539, 4617, 4694, 4771, 4848, 4924, 4999, 5075, 5150, 5224, 5299, 5372, 5446, 5519, 5591, 5664,
          5735, 5807, 5877, 5948, 6018, 6087, 6156, 6225, 6293, 6360, 6427, 6494, 6560, 6626, 6691, 6755, 6819,
          6883, 6946, 7009, 7071, 7132, 7193, 7253, 7313, 7372, 7431, 7489, 7547, 7604, 7660, 7716, 7771, 7826,
          7880, 7933, 7986, 8038, 8090, 8141, 8191, 8241, 8290, 8338, 8386, 8433, 8480, 8526, 8571, 8616, 8660,
          8703, 8746, 8788, 8829, 8870, 8910, 8949, 8987, 9025, 9063, 9099, 9135, 9170, 9205, 9238, 9271, 9304,
          9335, 9366, 9396, 9426, 9455, 9483, 9510, 9537, 9563, 9588, 9612, 9636, 9659, 9681, 9702, 9723, 9743,
          9762, 9781, 9799, 9816, 9832, 9848, 9862, 9876, 9890, 9902, 9914, 9925, 9935, 9945, 9953, 9961, 9969,
          9975, 9981, 9986, 9990, 9993, 9996, 9998, 9999, 10000]


# --------------------------------------------------------------------
# [GETARCCOS] Get the sinus and cosinus from the angle +/- multiple circles
# Cos4    	    - Input Cosinus
# AngleRad4 	- Output Angle in radials, decimals = 4
def GetArcCos(Cos4):

    log.debug("GetArcCos: Cos4=%s" % Cos4)
    # Check for negative value
    if Cos4 < 0:
        Cos4 = -Cos4
        NegativeValue = 1
    else:
        NegativeValue = 0

    if Cos4 >10000:
        Cos4 = 10000
        log.debug("GetArcCos: applied upper bound of 10000") 
        
    # Limit Cos4 to his maximal value
    Cos4 = max(Cos4, c4DEC)

    if 0 <= Cos4 < 9000:
        AngleRad4 = GetACos[int(Cos4/79)]            # 79=table resolution (1/127)
        AngleRad4 = AngleRad4*616/c1DEC         # 616=acos resolution (pi/2/255)

    elif 9000 <= Cos4 < 9900:
        AngleRad4 = GetACos[int((Cos4-9000)/8)+114]  # 8=table resolution (0.1/127), 114 start address 2nd bytetable range
        AngleRad4 = AngleRad4*616/c1DEC         # 616=acos resolution (pi/2/255)

    elif 9900 <= Cos4 <= 10000:
        AngleRad4 = GetACos[int((Cos4-9900)/2)+227]  # 2=table resolution (0.01/64), 227 start address 3rd bytetable range
        AngleRad4 = AngleRad4*616/c1DEC         # 616=acos resolution (pi/2/255)

    # Add negative sign
    if NegativeValue:
        AngleRad4 = 31416 - AngleRad4

    log.debug("GetArcCos: AngleRad4=%s" % AngleRad4)
    return AngleRad4


# --------------------------------------------------------------------
# [GETATAN2] Simplyfied ArcTan2 function based on fixed point ArcCos
# ArcTanX 		- Input X
# ArcTanY 		- Input Y
# ArcTan4  		- Output ARCTAN2(X/Y)
# XYhyp2		- Output presenting Hypotenuse of X and Y
def GetAtan2(AtanX, AtanY):
    log.debug("GetAtan2: AtanX=%s, AtanY=%s" % (AtanX, AtanY))
    
    XYhyp2 = math.sqrt((AtanX * AtanX * c4DEC) + (AtanY * AtanY * c4DEC))
    AngleRad4 = GetArcCos(AtanX * c6DEC / XYhyp2)

    if AtanY != 0:
        Atan4 = AngleRad4 * (AtanY / abs(AtanY))  # Add sign
    else:
        Atan4 = AngleRad4
        
    log.debug("GetAtan2: Atan4=%d, XYhyp2=%s" % (Atan4, XYhyp2))
    return Atan4, XYhyp2


# --------------------------------------------------------------------
# [GETSINCOS] Get the sinus and cosinus from the angle +/- multiple circles
# AngleDeg1 	- Input Angle in degrees, decimals = 1
# Sin4    	    - Output Sinus of the given Angle, decimals = 4
# Cos4  		- Output Cosinus of the given Angle, decimals = 4
def GetSinCos(AngleDeg1):

    # Get the absolute value of the Angle in Degrees, decimals = 1
    if AngleDeg1 < 0:
        ABSAngleDeg1 = AngleDeg1 * (-1)
    else:
        ABSAngleDeg1 = AngleDeg1

    # Shift rotation to a full circle of 360 deg -> AngleDeg // 360
    if AngleDeg1 < 0:   # Negative values
        AngleDeg1 = 3600 - (ABSAngleDeg1 - (3600 * (ABSAngleDeg1 / 3600)))
    else:				# Positive values
        AngleDeg1 = ABSAngleDeg1 - (3600 * (ABSAngleDeg1 / 3600))

    if 0 <= AngleDeg1 <= 900:                   # 0 to 90 deg
        Sin4 = GetSin[int(AngleDeg1 / 5)]		    # 5 is the presision (0.5) of the table
        Cos4 = GetSin[int((900 - AngleDeg1) / 5)]

    elif 900 < AngleDeg1 <= 1800:               # 90 to 180 deg
        Sin4 = GetSin[int((900-(AngleDeg1-900))/5)]  # 5 is the presision (0.5) of the table
        Cos4 = -GetSin[int((AngleDeg1-900)/5)]

    elif 1800 < AngleDeg1 <= 2700:              # 180 to 270 deg
        Sin4 = -GetSin[int((AngleDeg1-1800)/5)] 	    # 5 is the presision (0.5) of the table
        Cos4 = -GetSin[int((2700-AngleDeg1)/5)]

    elif 2700 < AngleDeg1 <= 3600:              # 270 to 360 deg
        Sin4 = -GetSin[int((3600-AngleDeg1)/5)]      # 5 is the presision (0.5) of the table
        Cos4 = GetSin[int((AngleDeg1-2700)/5)]

    return Sin4, Cos4
