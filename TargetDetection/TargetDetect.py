#####################################################################################################
# Credits for TargetDetect.py:                                                                      #
# The code for detecting the goal, and drawing on the image was created by Kevin Brandon. (Thanks!) #
# The rest of the code was created by the Epic Robotz Admin Web team.                               #
#####################################################################################################

#Import the necessary packages
from __future__ import print_function
from picamera.array import PiRGBArray
from picamera import PiCamera
from socket import *
from threading import Thread
from time import strftime
import math
import time
import cv2
import numpy as np
import os
import os.path
import threading
#
#Functions and Variables and Threads, oh my!
#
#Sets up listening and talking socket variables...
global host
host = ""
global port
port = 5800
global buf
buf = 1024
global addr
addr = (host, port)
global UDPSock
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)
#CommOutbound Function
def CommOutbound(recipiant, message):
	global logmsg
	global UDPSock
	UDPSock.bind(addr)
	if recipiant == "RPiConsole":
		print(message)
		#Log the communication stream:
		logmsg = time.strftime("%X") + " [INFO] Communication stream: RPi --> RPiConsole: " + message
		with open('log.txt', 'a') as f:
			print(logmsg, file=f)
		message = ""
		logmsg = ""
	elif recipiant == "RoboRio":
		message += "\r"
		sock.sendto(message, ("RoboRioIP"), 5800)
		#Log the communication stream:
		logmsg = strftime("%X") + " [INFO] Communication stream: RPi --> RoboRio: " + message
		with open('log.txt', 'a') as f:
			print(logmsg, file=f)
		message = ""
		logmsg = ""		
	elif recipiant == "Op":
		sock.sendto(message, ("OpIP"), 5800)
		#Log the communication stream:
		logmsg = strftime("%X") + " [INFO] Communication stream: RPi --> Op: " + message
		with open('log.txt', 'a') as f:
			print(logmsg, file=f)
		message = ""
		logmsg = ""
#CommInbound Thread / Function
def CommInbound():
	#ActiveComm variable
	global ActiveComm
	global logmsg
	global UDPSock
	global data
	global addr
	UDPSock.bind(addr)
	ActiveComm = False
	while True:
		#Code for listening goes HERE.
		(data, addr) = UDPSock.recvfrom(buf)
		message = data
		if message == "/go":
			logmsg = strftime("%X") + " [INFO] Communication stream: O --> RPi: " + message
			with open('log.txt', 'a') as f:
				print(logmsg, file=f)
			OpIP = addr[0]
			ActiveComm = True
			#START MAIN THREAD
			ThreadMain = Thread(target = MainThread)
			ThreadMain.start()
			thread.join()
		if ActiveComm == True:
			if message[:4] == "/ping":
				logmsg = strftime("%X") + " [INFO] Communication stream: RoboRio --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				pass #Send back the latest targeting data
			if message == "/halt":
				logmsg = strftime("%X") + " [INFO] Communication stream: Op --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				ActiveComm = False
			if message == "/download":
				logmsg = strftime("%X") + " [INFO] Communication stream: Op --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				pass #Send off log and pictures to Op Console
			if message == "/viewgo":
				logmsg = strftime("%X") + " [INFO] Communication stream: Op --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				pass #Start streaming image data to OpConsole
			if message == "/viewhalt":
				logmsg = strftime("%X") + " [INFO] Communication stream: Op --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				pass #Stop streaming image data to OpConsole
			if message[:6] == "/change":
				logmsg = strftime("%X") + " [INFO] Communication stream: Op --> RPi: " + message
				with open('log.txt', 'a') as f:
					print(logmsg, file=f)
				pass
			message = "" 
			logmsg = ""
			sendername = ""
# A call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass
# A function that checks the 4 sides of a quadrilatal, for goal detection in images.  
# If all 4 sides are close to horizontal or vertical (+/- epsilon) 
# AND make sure that the aspect ratio is within the tolerance
def CheckAnglesAndAspect(corners, epsilon, aspectRatio, aspectTolerance):
	#Require 4 corners
	if len(corners) != 4:
		return False
	sumWidth = 0	#Sum of the two horizontal sides
	sumHeight = 0	#Sum of the two vertical sides
	# loop through each corner
	for i in range(4):
		i0 = i 				# index to the first corner
		i1 = (i + 1) % 4	# index to the next corner
		x = abs(corners[i1][0][0] - corners[i0][0][0])	#The difference in x
		y = abs(corners[i1][0][1] - corners[i0][0][1])	#The difference in y
		length = math.sqrt(x**2 + y**2)					#The length of this side
		#If x > y, then it's mostly horizontal
		if x > y:	
			#The angle off horizontal
			theta = math.atan2(y,x) * 180 / math.pi
			#Add length to the sum of the width
			sumWidth += length
		else:
			#The angle off vertical 
			theta = math.atan2(x,y) * 180 / math.pi
			#Add length to the sum of the height
			sumHeight += length
		#If the angle is greater than epsilon, then it's not vertical or horizontal, so return false
		if abs(theta) > epsilon:
			return False
	#Calculate the average width and height
	avgWidth = sumWidth / 2
	avgHeight = sumHeight / 2
	#Calculate the expected height using the expected aspect ratio and the measured width
	expectedHeight = avgWidth / aspectRatio 
	#Check that the difference between the expected height and the actual height is less than the tolerance
	if abs(expectedHeight - avgHeight) > (aspectTolerance * expectedHeight):
		return False
	#If we get here then all corners have been checked and are okay.
	return True
#Some color values we'll be using
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
#Sets Camera FOV
CameraFOV = (160, 56)
#Sets Camera resolution
resolution = (640, 480)
#Gets the azmuith and elevation angles from a point in the image in degrees
def GetAzEl(point):
	az = point[0]/float(resolution[0]) - 0.5
	el = (1 - point[1]/float(resolution[1])) - 0.5
	return (az * CameraFOV[0], el * CameraFOV[1])
#Integer for naming files, and determining the picture settings - every tenth picture is taken with "normal" settings, while all other pictures have the optimal settings for goal detection.
imagecount = 0
#Interger which will be used, upon program halt, to calculate the average latentcy - or image process time
AverageLatentcy = 0
#
#Initialize program
#
#
#Start communication with Operator Console and RoboRio
#
#START LISTENING THREAD
ThreadListen = Thread(target = CommInbound)
ThreadListen.start()
#
#Start capturing and processing of images
#
#Try to initialize the camera and grab a reference to the raw camera capture.
def MainThread():
	#Print startup informaton to console.
	CommOutbound("RPiConsole", "[INFO] Initiating program... Press \"Ctrl + C\" to stop program execution.")
	CommOutbound("Op", "[INFO] Initiating program... Press \"Stop Program\" to remotely stop program execution.")
	CommOutbound("RPiConsole", "[INFO] Logging started!")
	CommOutbound("Op", "[INFO] Logging started!")
	CommOutbound("RPiConsole", "[INFO] Starting camera...")
	CommOutbound("Op", "[INFO] Starting camera...")
	try:
		camera = PiCamera()
		camera.resolution = resolution
		camera.shutter_speed = 10000
		camera.exposure_mode = 'off'
		rawCapture = PiRGBArray(camera, size=resolution)
		#Allow camera to start.
		time.sleep(0.5)
		CommOutbound("RPiConsole", "[INFO] Camera started!")
		CommOutbound("Op", "[INFO] Camera started!")
	except:
		CommOutbound("RPiConsole", "[FATL] Unable to start camera! Attempting to continue with program.")
		CommOutbound("Op", "[FATL] Unable to start camera! Attempting to continue with program.")
	#Capture frames from the camera
	CommOutbound("RPiConsole", "[INFO] Starting image capturing and processing...")
	CommOutbound("Op", "[INFO] Starting image capturing and processing...")
	while ActiveComm == True:
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			if imagecount % 10 == True:
				#
				#Runs with settings set for "regular picture mode"
				#
				#Start latentcy timer
				TimeStart = datetime.timetuple
				#
				#Set values for processing:
				#
				#Draw Threshold?
				drawThresh = 0
				#Use adaptive threshold?
				useAdaptive = 1
				#Set the threshold value
				thresh = 5
				#Set the minimum perimiter of a valid target (in pixel length)
				minPerim = 45
				#Set the target average pixel value in the image, used to set the shutter speed
				autoShutter = 40
				#Set the max angle we can be off for horizontal and vertical sides
				eps = 5
				#Set the aspect ratio of the target (width / height)
				aspect = 1.5
				#Set the aspect ratio tolerance in percetage
				aspectTol = 0.5
				#Set the adaptive threshold size.
				adaptiveSize = 3
				#Set the shutter speed.
				ss = camera.shutter_speed
			else:
				#
				#Runs with settings set for optimal goaldetection conditions
				#
				#Start latentcy timer
				TimeStart = datetime.timetuple
				#
				#Set values for processing:
				#
				#Draw Threshold?
				drawThresh = 1
				#Use adaptive threshold?
				useAdaptive = 1
				#Set the threshold value
				thresh = 5
				#Set the minimum perimiter of a valid target (in pixel length)
				minPerim = 45
				#Set the target average pixel value in the image, used to set the shutter speed
				autoShutter = 40
				#Set the max angle we can be off for horizontal and vertical sides
				eps = 5
				#Set the aspect ratio of the target (width / height)
				aspect = 1.5
				#Set the aspect ratio tolerance in percetage
				aspectTol = 0.5
				#Set the adaptive threshold size.
				adaptiveSize = 3
				#Set the shutter speed.
				ss = camera.shutter_speed
			#
			#Process image
			#
			#Grab the raw NumPy array representing the image
			drawnImage = image = frame.array
			#Convert to a grayscale image
			gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			#Calculate the avarage pixel value
			avg = cv2.mean(gray_image)
			#Threshold the grayscale image
			if useAdaptive == 0:
				#Use the simple global threshold routine
				ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
			else:
				#Use the fancy adaptive threshold routine
				threshImg = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, adaptiveSize, thresh)
			#If value is set to 1, use the threshold image to draw on instead of the original
			if drawThresh == 1:
				#Convert the threshold image back to color so we can draw on it with colorful lines
				drawnImage = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2RGB)
			#Find the contours in the thresholded image...
			im2, contours, high = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
			#The arrays of detected targets, they're empty now, but we'll fill them next.
			finalTargets = []
			#For each contour we found...
			for cnt in contours:
				#Get the convexHull
				hull = cv2.convexHull(cnt)
				#Get the perimiter of the hull.
				perim = cv2.arcLength(hull, True)
				#Is the the perimiter of the hull is > than the minimum allowed?
				if perim >= minPerim: 
					#Approximate the hull:
					aproxHull = cv2.approxPolyDP(hull, 0.1 * perim, True)
					#Only add this target if it has 4 verticies
					if len(aproxHull) == 4:
						#Check to see if the 4 sides are near horizontal or vertical, and check the aspect ratio
						if CheckAnglesAndAspect(aproxHull, eps, aspect, aspectTol):
							#Add the contour to the list of final targets
							finalTargets.append(aproxHull)
			#Draw on top of the original image...
			#Draw all the detected hulls back on the original image (green with a width of 3)
			cv2.drawContours(drawnImage, finalTargets, -1, blue, 3)
			#Find the center of each target:
			for target in finalTargets:
				#Find it's moments:  
				M = cv2.moments(target)
				#Get the center x and y values...
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])
				#Get the angles to the target
				angles = GetAzEl((cx, cy))
				#Draw the angles on the screen
				text = '(%.0f,%0.f)' % angles
				cv2.putText(drawnImage, text, (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.33, green, 1)
				#Draw a little crosshair at the center of the target
				cv2.line(drawnImage, (cx-2, cy), (cx+2, cy), red, 1)	# little horizontal line
				cv2.line(drawnImage, (cx, cy-2), (cx, cy+2), red, 1)	# little vertical line
			#Draw number of detections found on image
			text = 'Number of detections: %d' % (len(finalTargets))
			cv2.putText(drawnImage, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
			#Write the image into the datadump directory
			imagecount = imagecount + 1
			imagename = 'TargetImage_' + str(imagecount) + '.jpg'
			cv2.imwrite(imagename,drawnImage)
			CommOutbound("RPiConsole", "[INFO] Image captured: " + imagename + ".")
			CommOutbound("Op", "[INFO] Image captured: " + imagename + ".")
			#Clear the stream in preparation for the next frame
			rawCapture.truncate(0)
			#Calculate the increment for the shutter speed by 1% of it's current value
			inc = 0
			if avg[0] > (autoShutter + 2):
				inc = -max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
			if avg[0] < (autoShutter - 2):
				inc = max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
			#Set the shutter speed
			camera.shutter_speed = ss + inc
			#Stop Latentcy timer
			TimeEnd = datetime.timetuple
			Latentcy = math.ceil((TimeEnd - TimeStart))
			#Add this times latentcy to AverageLatentcy variable
			AverageLatentcy += Latentcy
			if len(finalTargets) == 0:
				CommOutbound("RPiConsole", "[INFO] No goal was detected in image \"" + imagename + "\".")
				CommOutbound("Op", "[INFO] No goal was detected in image \"" + imagename + "\".")
			else:
				CommOutbound("RPiConsole", "[INFO] " + str(len(finalTargets)) + " targets were detected in \"" + imagename + "\"! Sending information to RoboRio module...")
				CommOutbound("Op", "[INFO] " + str(len(finalTargets)) + " targets were detected in \"" + imagename + "\"! Sending information to RoboRio module...")
				#
				#SEND INFORMATION TO ROBORIO, AND LOG THAT INFORMATION WAS SENT, ALONG WITH A COPY OF THAT INFORMATION! (Both to console and to log file.)
				#
				message = "(" + str(angles) + ")"
				CommOutbound("RPiConsole", "[INFO] Communication stream: RPi --> RPiConsole: " + message)
				CommOutbound("Op", "[INFO] Communication stream: RPi --> Op: " + message)
				#CommOutbound("RoboRio", "[INFO] Communication stream: RPi --> RoboRio: " + message)
			#Reset values for TimeStart, TimeEnd, and latentcy
			TimeStart = 0
			TimeEnd = 0
			Latentcy = 0
	message = "[INFO] Program inturrupt signal detected! Stopping program..."
	CommOutbound("RPiConsole", "[INFO] " + message)
	CommOutbound("Op", "[INFO] " + message)
	#Record average latentcy
	AverageLatentcy = AverageLatentcy / imagecount
	message = "Average image process time: " + AverageLatentcy + "."
	CommOutbound("RPiConsole", "[INFO] Communication stream: RPi --> RPiConsole: " + message)
	CommOutbound("Op", "[INFO] " + message)
	#Stop of program message
	CommOutbound("RPiConsole", "[INFO] Program execution halting NOW.")
