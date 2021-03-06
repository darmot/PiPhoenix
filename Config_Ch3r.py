# Project Lynxmotion Phoenix
# Description: chr-3, configuration file.
#       All Hardware connections (excl controls) and body dimensions 
#       are configurated in this file. Can be used with V2.0 and above
# Configuration version: V1.0
# Date: Nov 1, 2009
# Programmer: Kurt (aka KurtE)
# 
# Hardware setup: ABB2 with ATOM 28 Pro, SSC32 V2, (See further for connections)
# 
# NEW IN V1.0
#    - First Release
# 
# --------------------------------------------------------------------
# [SERIAL CONNECTIONS]
# cSSC_OUT         con P10      # Output pin for (SSC32 RX) on BotBoard (Yellow)
# cSSC_IN          con P11      # Input pin for (SSC32 TX) on BotBoard (Blue)
cSSC_BAUD      = 115200  # SSC32 BAUD rate
# --------------------------------------------------------------------
# [BB2 PIN NUMBERS]
# cEyesPin      con P8
# --------------------------------------------------------------------
# [SSC PIN NUMBERS]
cRRCoxaPin     = "0"    # Rear Right leg Hip Horizontal
cRRFemurPin    = "1"    # Rear Right leg Hip Vertical
cRRTibiaPin    = "2"    # Rear Right leg Knee

cRMCoxaPin     = "4"    # Middle Right leg Hip Horizontal
cRMFemurPin    = "5"    # Middle Right leg Hip Vertical
cRMTibiaPin    = "6"    # Middle Right leg Knee

cRFCoxaPin     = "8"    # Front Right leg Hip Horizontal
cRFFemurPin    = "9"    # Front Right leg Hip Vertical
cRFTibiaPin    = "10"   # Front Right leg Knee

cLRCoxaPin     = "16"   # Rear Left leg Hip Horizontal
cLRFemurPin    = "17"   # Rear Left leg Hip Vertical
cLRTibiaPin    = "18"   # Rear Left leg Knee

cLMCoxaPin     = "20"   # Middle Left leg Hip Horizontal
cLMFemurPin    = "21"   # Middle Left leg Hip Vertical
cLMTibiaPin    = "22"   # Middle Left leg Knee

cLFCoxaPin     = "24"   # Front Left leg Hip Horizontal
cLFFemurPin    = "25"   # Front Left leg Hip Vertical
cLFTibiaPin    = "26"   # Front Left leg Knee
# --------------------------------------------------------------------
# [MIN/MAX ANGLES]
cRRCoxaMin1    = -750      # Mechanical limits of the Right Rear Leg
cRRCoxaMax1    = 750
cRRFemurMin1   = -900
cRRFemurMax1   = 550
cRRTibiaMin1   = -400
cRRTibiaMax1   = 750

cRMCoxaMin1    = -750      # Mechanical limits of the Right Middle Leg
cRMCoxaMax1    = 750
cRMFemurMin1   = -900
cRMFemurMax1   = 550
cRMTibiaMin1   = -400
cRMTibiaMax1   = 750

cRFCoxaMin1    = -750      # Mechanical limits of the Right Front Leg
cRFCoxaMax1    = 750
cRFFemurMin1   = -900
cRFFemurMax1   = 550
cRFTibiaMin1   = -400
cRFTibiaMax1   = 750

cLRCoxaMin1    = -750      # Mechanical limits of the Left Rear Leg
cLRCoxaMax1    = 750
cLRFemurMin1   = -900
cLRFemurMax1   = 550
cLRTibiaMin1   = -400
cLRTibiaMax1   = 750

cLMCoxaMin1    = -750      # Mechanical limits of the Left Middle Leg
cLMCoxaMax1    = 750
cLMFemurMin1   = -900
cLMFemurMax1   = 550
cLMTibiaMin1   = -400
cLMTibiaMax1   = 750

cLFCoxaMin1    = -750      # Mechanical limits of the Left Front Leg
cLFCoxaMax1    = 750
cLFFemurMin1   = -900
cLFFemurMax1   = 550
cLFTibiaMin1   = -400
cLFTibiaMax1   = 750
# --------------------------------------------------------------------
# [BODY DIMENSIONS]
cCoxaLength      =  29     # 1.14" = 29mm (1.14 * 25.4)
cFemurLength     =  57     # 2.25" = 57mm (2.25 * 25.4)
cTibiaLength     = 141     # 5.55" = 141mm (5.55 * 25.4)

cRRCoxaAngle1    = -600    # Default Coxa setup angle, decimals = 1
cRMCoxaAngle1    = 0       # Default Coxa setup angle, decimals = 1
cRFCoxaAngle1    = 600     # Default Coxa setup angle, decimals = 1
cLRCoxaAngle1    = -600    # Default Coxa setup angle, decimals = 1
cLMCoxaAngle1    = 0       # Default Coxa setup angle, decimals = 1
cLFCoxaAngle1    = 600     # Default Coxa setup angle, decimals = 1

cRROffsetX       = -69     # Distance X from center of the body to the Right Rear coxa
cRROffsetZ       = 119     # Distance Z from center of the body to the Right Rear coxa
cRMOffsetX       = -138    # Distance X from center of the body to the Right Middle coxa
cRMOffsetZ       = 0       # Distance Z from center of the body to the Right Middle coxa
cRFOffsetX       = -69     # Distance X from center of the body to the Right Front coxa
cRFOffsetZ       = -119    # Distance Z from center of the body to the Right Front coxa

cLROffsetX       = 69      # Distance X from center of the body to the Left Rear coxa
cLROffsetZ       = 119     # Distance Z from center of the body to the Left Rear coxa
cLMOffsetX       = 138     # Distance X from center of the body to the Left Middle coxa
cLMOffsetZ       = 0       # Distance Z from center of the body to the Left Middle coxa
cLFOffsetX       = 69      # Distance X from center of the body to the Left Front coxa
cLFOffsetZ       = -119    # Distance Z from center of the body to the Left Front coxa

# --------------------------------------------------------------------
# [START POSITIONS FEET]
cRRInitPosX    = 53      # Start positions of the Right Rear leg
cRRInitPosY    = 25
cRRInitPosZ    = 91

cRMInitPosX    = 105      # Start positions of the Right Middle leg
cRMInitPosY    = 25
cRMInitPosZ    = 0

cRFInitPosX    = 53      # Start positions of the Right Front leg
cRFInitPosY    = 25
cRFInitPosZ    = -91

cLRInitPosX    = 53      # Start positions of the Left Rear leg
cLRInitPosY    = 25
cLRInitPosZ    = 91

cLMInitPosX    = 105      # Start positions of the Left Middle leg
cLMInitPosY    = 25
cLMInitPosZ    = 0

cLFInitPosX    = 53      # Start positions of the Left Front leg
cLFInitPosY    = 25
cLFInitPosZ    = -91
# --------------------------------------------------------------------
