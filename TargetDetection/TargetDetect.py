# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import time
import cv2
import numpy as np
import os
#Print startup informaton to user console.
print '[INFO] Program initiated!'
print '[INFO] Press "Ctrl + C" to halt program execution at any time.'
print '[INFO] Starting communication with RoboRio module...'
#Send start of transmission feed character "/" to the RoboRio.
#Format is: "@(X,Y)(X,Y)(X,Y)#", with "@" indicating the start of a transmission feed, and "()" marking individual "packets" of information; in this case, X and Y values, conveying the position of the robot in relation to the center of the goal.
#"#" indicates the end of a transmission feed, and is sent when the program is halted.
#Put an IF statement here to see if communication is working correctly. When the RoboRio sees the "@" it should send back a message telling the program that it indeed sees the connection. Then we'll begin the rest of our script...
print '[INFO] Started communication with RoboRio module.'
# a call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass
print '[INFO] Creating functions and variables...'
# a function that checks the 4 sides of a quadrilatal, for goal detection in images.  
# If all 4 sides are close to horizontal or vertical (+/- epsilon) 
# AND make sure that the aspect ratio is within the tolerance
def CheckAnglesAndAspect(corners, epsilon, aspectRatio, aspectTolerance):
	# require 4 corners
	if len(corners) != 4:
		return False
	sumWidth = 0	# sum of the two horizontal sides
	sumHeight = 0	# sum of the two vertical sides
	# loop through each corner
	for i in range(4):
		i0 = i 				# index to the first corner
		i1 = (i + 1) % 4	# index to the next corner
		x = abs(corners[i1][0][0] - corners[i0][0][0])	# the difference in x
		y = abs(corners[i1][0][1] - corners[i0][0][1])	# the difference in y
		length = math.sqrt(x**2 + y**2)					# the length of this side
		# if x > y, then it's mostly horizontal
		if x > y:	
			# the angle off horizontal
			theta = math.atan2(y,x) * 180 / math.pi
			# add length to the sum of the width
			sumWidth += length
		else:
			# the angle off vertical 
			theta = math.atan2(x,y) * 180 / math.pi
			# add length to the sum of the height
			sumHeight += length
		# if the angle is greater than epsilon, then it's not vertical or horizontal, so return false
		if abs(theta) > epsilon:
			return False
	# calculate the average width and height
	avgWidth = sumWidth / 2
	avgHeight = sumHeight / 2
	# calculate the expected height using the expected aspect ratio and the measured width
	expectedHeight = avgWidth / aspectRatio 
	# check that the difference between the expected height and the actual height is less than the tolerance
	if abs(expectedHeight - avgHeight) > (aspectTolerance * expectedHeight):
		return False
	# if we get here then all corners have been checked and are okay.
	return True
#some color values we'll be using
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
# Sets Camera FOV
CameraFOV = (160, 56)
# Sets Camera resolution
resolution = (640, 480)
# gets the azmuith and elevation angles from a point in the image in degrees
def GetAzEl(point):
	az = point[0]/float(resolution[0]) - 0.5
	el = (1 - point[1]/float(resolution[1])) - 0.5
	return (az * CameraFOV[0], el * CameraFOV[1])
# Integer for naming files.
i = 0
print '[INFO] Functions and variables created!'
print '[INFO] Starting camera...'
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = resolution
camera.shutter_speed = 10000
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=resolution)
#Allow camera to start.
time.sleep(0.5)
print '[INFO] Camera started!'
print '[INFO] Image taking and processing started!'
# Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
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
	
	# grab the raw NumPy array representing the image
	drawnImage = image = frame.array
	# convert to a grayscale image
	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# calculate the avarage pixel value
	avg = cv2.mean(gray_image)
	# threshold the grayscale image
	if useAdaptive == 0:
		#use the simple global threshold routine
		ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
	else:
		# use the fancy adaptive threshold routine
		threshImg = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, adaptiveSize, thresh)
	# if value is set to 1, use the threshold image to draw on instead of the original
	if drawThresh == 1:
		# convert the threshold image back to color so we can draw on it with colorful lines
		drawnImage = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2RGB)
	# find the contours in the thresholded image...
	im2, contours, high = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	# the arrays of detected targets, they're empty now, but we'll fill them next.
	finalTargets = []
	# for each contour we found...
	for cnt in contours:
		# get the convexHull
		hull = cv2.convexHull(cnt)
		# get the perimiter of the hull
		perim = cv2.arcLength(hull, True)
		# is the the perimiter of the hull is > than the minimum allowed?
		if perim >= minPerim: 
			#approximate the hull:
			aproxHull = cv2.approxPolyDP(hull, 0.1 * perim, True)
			# only add this target if it has 4 verticies
			if len(aproxHull) == 4:
				# check to see if the 4 sides are near horizontal or vertical, and check the aspect ratio
				if CheckAnglesAndAspect(aproxHull, eps, aspect, aspectTol):
					# add the contour to the list of final targets
					finalTargets.append(aproxHull)
	#Draw on top of the original image...
	# draw all the detected hulls back on the original image (green with a width of 3)
	cv2.drawContours(drawnImage, finalTargets, -1, blue, 3)
	# Find the center of each target:
	for target in finalTargets:
		# find it's moments:  
		M = cv2.moments(target)
		# get the center x and y values...
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		# get the angles to the target
		angles = GetAzEl((cx, cy))
		# draw the angles on the screen
		text = '(%.0f,%0.f)' % angles
		cv2.putText(drawnImage, text, (cx + 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.33, green, 1)
		# draw a little crosshair at the center of the target
		cv2.line(drawnImage, (cx-2, cy), (cx+2, cy), red, 1)	# little horizontal line
		cv2.line(drawnImage, (cx, cy-2), (cx, cy+2), red, 1)	# little vertical line
	#Draw number of detections found on image
	text = 'Number of detections: %d' % (len(finalTargets))
	cv2.putText(drawnImage, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	#Write the image into the datadump directory
        i = i + 1
	imagename = 'TargetImage_' + str(i) + '.jpg'
        cv2.imwrite(imagename,drawnImage)

	# Important!  Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 	# calculate the increment for the shutter speed by 1% of it's current value
 	inc = 0
	if avg[0] > (autoShutter + 2):
	 	inc = -max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
	if avg[0] < (autoShutter - 2):
	 	inc = max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
	# set the shutter speed
	camera.shutter_speed = ss + inc
	#Stop Latentcy timer
        TimeEnd = time.time()
        Latentcy = math.ceil((TimeEnd - TimeStart)*100)
        print 'Latentcy: ' + str(Latentcy)
        #Reset values for timestart and timeend
        TimeStart = 0
        TimeEnd = 0
        Latentcy = 0
	#Send information to RoboRio: "angles" variable (see above), perhaps along with the latentcy...
