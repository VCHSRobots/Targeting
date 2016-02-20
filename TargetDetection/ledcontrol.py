import RPi.GPIO as GPIO
import time
import os


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

def setwires( v ):
	if v & 1 != 0:
		GPIO.output(36, True)
	else:
		GPIO.output(36, False)
	if v & 2 != 0:
		GPIO.output(38, True)
	else:
		GPIO.output(38, False)
	if v & 4 != 0:
		GPIO.output(40, True)
	else:
		GPIO.output(40, False)
	return

while (True):
	for i in range(8):
		setwires(i)
		time.sleep(1)
