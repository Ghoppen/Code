import serial
import time

port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1) 

port.write('AT'+'\r\n')
time.sleep(.1)

port.write('AT+CGNSPWR=1'+'\r\n')
time.sleep(.1)

port.write('AT+CGNSIPR=115200'+'\r\n')
time.sleep(.1)

port.write('AT+CGNSTST=1'+'\r\n')
time.sleep(.1)

port.write('AT+CGNSINF'+'\r\n')
time.sleep(.1)
