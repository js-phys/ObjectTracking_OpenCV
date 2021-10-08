# -*- coding: utf-8 -*-
"""
Detect the biggest object with red color and track it. Coordinates, i.e. its trajectory can be saved.
Press 's' on keyboard to start the detection.
Interrupt by pressing 'q' on keyboard.
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt

def get_speed(x, x2, s, s2):
    deltas = s-s2
    deltax = x-x2    
    if deltas > 0.0:
        return deltax/deltas 
    else:
        return 0.0

# Determine what red color means
# CorelDraw HSV uses H = 0-360,   S = 0-100   and V = 0-100. 
# But OpenCV uses    H = 0 - 180, S = 0 - 255 and V = 0 - 255
RED_MIN = np.array([2, 100, 100],np.uint8)
RED_MAX = np.array([6, 250, 250],np.uint8)

# set the artefact threshold in pixel size
artefacts = 100
#set the region of interest rectangle (visualized by green rectangle)
roi_upperleft = (620,50)
roi_bottomright = (1580,1000)

# initialize counter and variables
without_object = 0
start_calc = 0
#last_cX = 0 only necessary if velocity calculation is done
#last_cY = 0

# initialize list for every quantity which is extracted to file
time_s = []
frame_nr = []
coord_x = []
coord_y = []
velocity_x = []
velocity_y = []

#open video and get some information
cap = cv2.VideoCapture('test.MOV')
total_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))

print cap

while True:  
    # Read a frame of the video
    grabbed, frame = cap.read()
    key = cv2.waitKey(1) & 0xFF
       
    
    # if the frame could not be grabbed, then we have reached the end of the video
    if not grabbed:
        print "Video ended"
        break    
    
    # get actual frame and playtime
    f_nr = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
    seconds = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000 
    
    #put some information to the displayed video
    cv2.putText(frame, "seconds {0:.3f}".format(seconds), (900,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "fps {0:.2f}".format(fps), (1800,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.rectangle(frame, roi_upperleft, roi_bottomright, (0, 255, 0), 1) #define this region as roi
    
    # process frame
    hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    frame_threshed = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(frame_threshed, None, iterations=2)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    
    #set start_calc if s button is pressed, before s was pressed no visualization of the moving object
    if (key == ord('s')):
        start_calc = 1
        last_cX =0
        last_s=0
    # find largest contour and draw it
    elif (len(contours) > 0) and (start_calc == 1):        
        #create array for contours 
        areaArray = []
        for i, c in enumerate(contours):
            area = cv2.contourArea(c)
            areaArray.append(area)
            

        #first sort the array by area
        sorteddata = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)
    
        #find the nth largest contour [n-1][1], in this case the 1st
        largestcontour = sorteddata[0][1]
        
        # prevent division by zero
        M = cv2.moments(largestcontour)
        if (M["m00"] == 0):
            M["m00"]=1
        #calculate centerpoint of contour
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        
        #filter artifacts and
        #store the centerpoint and related data
        if cv2.contourArea(largestcontour) > artefacts:
            coord_x.append(cX)
            coord_y.append(cY)
            frame_nr.append(f_nr)
            time_s.append(seconds)  
        
        #draw centerpoint and put text of x,y coordinates
        cv2.circle(frame, (cX,cY), 1, (0,255,0), 2)
        text = '{} {}'.format(cX, cY)
        cv2.putText(frame, text, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2) 
        
        #draw hull of largestarea
        x, y, w, h = cv2.boundingRect(largestcontour)
        hull = cv2.convexHull(largestcontour)
        cv2.drawContours(frame,[hull], 0,(0,0,255),2)
        
        # calculate speed with last frame
        #speed_x = get_speed(cX, last_cX, seconds, last_s)     
        #speed_y = get_speed(cY, last_cY, seconds, last_s)
            
        #cv2.putText(frame, "speed x {}".format(speed_x), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #cv2.putText(frame, "speed y {}".format(speed_y), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #store last centerpoint values
        #last_cX = cX
        #last_cY = cY
        #last_s = seconds
        #store speed
        #velocity_x.append(speed_x)
        #velocity_y.append(speed_y)
        out.write(frame)
    else:
        # if no contour was found = no red object in frame
        without_object += 1
        
    #Put text about missing frames        
    #cv2.putText(frame, "Frames without object = {}".format(without_object), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
   
      
    
    # show video
    smallerim = cv2.resize(frame, (960,540))
    cv2.imshow('Video', smallerim)
    
    # quit video with pressing q
    if key == ord('q'):
        break

plt.plot(time_s, coord_x)

cap.release()
cv2.destroyAllWindows()