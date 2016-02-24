#####################################################################################################
# Credits:                                                                                          #
# The code for detecting the goal, and drawing on the image was created by Kevin Brandon. (Thanks!) #
# The rest of the code was created by the EpicRobotz Admin Web team.                                #
#####################################################################################################

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import time
import cv2
import numpy as np
import os
#Print startup informaton to console.
print '[INFO] Program initiated!'
print '[INFO] Press "ESC" to halt program execution.'
print '[INFO] Starting program logging...'
print '[INFO] Program logging started!'
print(time.strftime("%H:%M:%S") + " [INFO] Program logging started!", file=log.txt)
print '[INFO] Starting communication with RoboRio module...'
print(time.strftime("%H:%M:%S") + " [INFO] Starting communication with RoboRio module...", file=log.txt)

#######################################################################################################################################################################################################################################################
# Send start of transmission feed character "/" to the RoboRio.                                                                                                                                                                                        #
# Format is: "@(X,Y)(X,Y)(X,Y)#", with "@" indicating the start of a transmission feed, and "()" marking individual "packets" of information; in this case, X and Y values, conveying the position of the robot in relation to the center of the goal. #
# "#" indicates the end of a transmission feed, and is sent when the program is halted.                                                                                                                                                                #
# Put an IF statement here to see if communication is working correctly. When the RoboRio sees the "@" it should send back a message telling the program that it indeed sees the connection. Then we'll begin the rest of our script...                #
#                                                                                                                                                                                                                                                      #
# Here is some psudo-code:                                                                                                                                                                                                                             #
#                                                                                                                                                                                                                                                      #
#  string message = "@";                                                                                                                                                                                                                               #
#  send(message);                                                                                                                                                                                                                                      #
#  if (reply == "@(I see you!)#")                                                                                                                                                                                                                      #
#  	{                                                                                                                                                                                                                                                 #
# 	 Continue_With_Program                                                                                                                                                                                                                            #
# 	}                                                                                                                                                                                                                                                 #
#  else                                                                                                                                                                                                                                                #
#  	{                                                                                                                                                                                                                                                 #
# 	 DeleteSystem32... or provide an error message.                                                                                                                                                                                                   #
# 	}                                                                                                                                                                                                                                                 #
#######################################################################################################################################################################################################################################################

#Here are several outputs based upon the RoboRio's possible responses:
#print '[WARN] Connection to RoboRio module taking longer than 1 second'
#print '[FATL] Unable to start communication with RoboRio module: connection timeout.'
#print '[FATL] Unable to start communication with RoboRio module: bad response.'
print '[INFO] Started communication with RoboRio module.'
print(time.strftime("%H:%M:%S") + " [INFO] Started communication with RoboRio module.", file=log.txt)
# A call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass
print '[INFO] Creating functions and variables...'
print(time.strftime("%H:%M:%S") + " [INFO] Creating functions and variables...", file=log.txt)
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
# Integer for naming files, and determining the picture settings - every tenth picture is taken with "normal" settings, while all other pictures have the optimal settings for goal detection.
imagecount = 0
# Interget which will be used, upon program halt, to calculate the average latentcy - or image process time
AverageLatentcy = 0
print '[INFO] Functions and variables created!'
print(time.strftime("%H:%M:%S") + " [INFO] Functions and variables created!", file=log.txt)
print '[INFO] Starting camera...'
print(time.strftime("%H:%M:%S") + " [INFO] Starting camera...", file=log.txt)
#Initialize the camera and grab a reference to the raw camera capture.
camera = PiCamera()
camera.resolution = resolution
camera.shutter_speed = 10000
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=resolution)
#Allow camera to start.
time.sleep(0.5)
print '[INFO] Camera started!'
print(time.strftime("%H:%M:%S") + " [INFO] Camera started!", file=log.txt)
print '[INFO] Image taking and processing started!'
print(time.strftime("%H:%M:%S") + " [INFO] Image taking and processing started!", file=log.txt)
#Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	if i % 10 == true:
		#
		#Runs with settings set for "regular picture mode"
		#
		#Start latentcy timer
		TimeStart = time.time()
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
		TimeStart = time.time()
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
	imagename = 'TargetImage_' + str(i) + '.jpg'
	cv2.imwrite(imagename,drawnImage)
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
	TimeEnd = time.time()
	Latentcy = math.ceil((TimeEnd - TimeStart))
	#Add this times latentcy to AverageLatentcy variable
	AverageLatentcy += Latentcy
	#print 'Latentcy: ' + str(Latentcy)
	print '[INFO] Image captured and processed: ' + imagename + '.'
	print(time.strftime("%H:%M:%S") + " [INFO] Image captured and processed: " + imagename + ".", file=log.txt)
	if finalTargets == 0:
		print '[INFO] No targets were detected in image ' + imagename + '.'
		print(time.strftime("%H:%M:%S") + " [INFO] No targets were detected in image " + imagename + ".", file=log.txt)
	else:
		print '[INFO] A total of ' finalTargets + 'targets were detected in ' + imagename + '.'
		print(time.strftime("%H:%M:%S") + " [INFO] A total of " finalTargets + "targets were detected in " + imagename + ".", file=log.txt)
		#
		#SEND INFORMATION TO ROBORIO, AND LOG THAT INFORMATION WAS SENT, ALONG WITH A COPY OF THAT INFORMATION! (Both to console and to log file.)
		#
		#Potential example below:
		#[INFO] Communication stream: Pi --> RoboRio : (VARIABLE1,VARIABLE2)
	#Reset values for TimeStart, TimeEnd, and latentcy
	TimeStart = 0
	TimeEnd = 0
	Latentcy = 0
	if key == 27:
		break
print '[INFO] Abort program key press detected! Stopping program...'
print(time.strftime("%H:%M:%S") + " [INFO] Abort program key press detected! Stopping program...", file=log.txt)
print '[INFO] Letting the RoboRio module know that program is stopping; sending end-of-stream signal...'.
print(time.strftime("%H:%M:%S") + " [INFO] Letting the RoboRio module know that program is stopping; sending end-of-stream signal...", file=log.txt)
# Add in responses to other roborio reactions HERE.
print '[INFO] RoboRio acknowledged end-of-stream signal; stream closed.'
print(time.strftime("%H:%M:%S") + " [INFO] RoboRio acknowledged end-of-stream signal; stream closed.", file=log.txt)
#Put code for roborio communication HERE.
#Calculates average latentcy
AverageLatentcy = AverageLatentcy / imagecount
print '[INFO] Average image process time was ' + AverageLatentcy + '.'
print(time.strftime("%H:%M:%S") + " [INFO] Average image process time was " + AverageLatentcy + ".", file=log.txt)
print '[INFO] Program stopped!'
print(time.strftime("%H:%M:%S") + " [INFO] Program stopped!, file=log.txt)