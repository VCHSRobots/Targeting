import time 
import sys
import spidev

spi = spidev.SpiDev()
spi.open(0,0)
while True:
	resp = spi.xfer2([0x45,0x70,0x69,0x63])
#	print resp[0]
	time.sleep(0.5)
	
