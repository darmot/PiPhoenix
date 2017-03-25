import serial

ser=serial.Serial('/dev/ttyUSB0', 115200)
ser.write('VER\n')
ser.read_until(serial.CR)
