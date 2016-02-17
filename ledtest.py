import string
import sys
import os
import serial
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
GPIO.output(11, True)

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)

while True:
	s = ""
	while True:
		s = s + ser.read()
		i = string.find(s, "\n")
		if i >= 0:
              		break
	print(s)

#	sys.stdout.write(x)
#	ser.read(10)	
#	ser.close()
