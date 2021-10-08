# -*- coding: utf-8 -*-
"""
Watch all videos in folder and track the biggest red object (Same as 'DetectRed.py')
Interrupt by pressing 'q' on keyboard
"""

import cv2
import numpy as np
import os
import datetime


# Determine what red color means
# CorelDraw HSV uses H = 0-360,   S = 0-100   and V = 0-100. 
# But OpenCV uses    H = 0 - 180, S = 0 - 255 and V = 0 - 255
RED_MIN = np.array([0, 10, 10],np.uint8)
RED_MAX = np.array([20, 250, 250],np.uint8)

# set the artifact threshold in pixel size
artefacts = 100

stopbutton = 0
cv2.namedWindow('Tracking in process')

#set working directory
dir = 'I:\+ PEOPLE\Johannes\V-shaped particle\+ Arc swimmer\Videos10032017_Arc_perp2'
os.chdir(dir)

#get all files in folder with ending .MOV
files = []
for file in os.listdir(os.getcwd()):
    if file.endswith(".MOV"):
        files.append(file)
        

###########start tracking for actual video
#initialize counter for videos
count_vids = 1

for actual_vid in files:
    start_time = datetime.datetime.now()
    #check if q was pressed, if so then exit program
    if stopbutton == 1:
        break
    
    #get name of video and print message to user
    basename = actual_vid.rsplit( ".", 1 )[0]
    print( 'Video {} of {}'.format(count_vids, len(files)) + ' is being processed ({})'.format(actual_vid) + '\n'
            'Please wait or abort by pressing q ...' )

    #open video and get some information
    cap = cv2.VideoCapture(actual_vid)
    total_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    
    # initialize counter for frames w/o object
    without_object = 0    
    
    # initialize list for every quantity which is extracted to file
    time_s = []
    frame_nr = []
    coord_x = []
    coord_y = []
    
    
    while True:  
        # Read a frame of the video
        grabbed, frame = cap.read()
        key = cv2.waitKey(1) & 0xFF
        
        # if the frame could not be grabbed, then we have reached the end of the video
        if not grabbed:
            print "Processing " + actual_vid + " ended"
            count_vids += 1
            break    
        
        # get actaul frame and playtime
        f_nr = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        seconds = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000 
        
        # process frame
        hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        frame_threshed = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(frame_threshed, None, iterations=2)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour and draw it
        if (len(contours) > 0):        
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
            
            #filter artefacts and
            #store the centerpoint and related data
            if cv2.contourArea(largestcontour) > artefacts:
                coord_x.append(cX)
                coord_y.append(cY)
                frame_nr.append(f_nr)
                time_s.append(seconds)
                   
        else:
            # if no contour was found = no red object in frame
            without_object += 1
            
        # quit process by pressing q
        if key == ord('q'):
            stopbutton = 1
            break
        
    #end processing of actual video
    cap.release()
    
    #get actual time
    endtime = datetime.datetime.now()
    elapsed = endtime - start_time  
    el_time = divmod(elapsed.total_seconds(),60)
    print 'Elapsed time: {} Min {} Secs'.format(el_time[0], el_time[1])
    
    # write header for output_file
    head = ('Created    ' + str(endtime.strftime("%Y-%m-%d %H:%M:%S")) + '\n'    
            'Video      ' + str(actual_vid) + '\n'
            'Frames     ' + str(f_nr) + '\n'
            'fps        ' + str("%.2f" % fps) + '\n'
            'Frames w/o object: ' + str(without_object) +'\n' + '\n'
            #specify column headers            
            'Second;' +'Frame;' + 'cX;' + 'cY;'                        
            )
    
    # write warning to file if aborted         
    if stopbutton == 1:
        head = 'WARNING! Tracking aborted before end of Video was reached' + '\n' + head
        print( "Aborted during tracking of Video {}".format(actual_vid) + '\n' +
               '{} Videos processed: '.format(count_vids-1) + str(files[:count_vids-1]) + '\n'
               '{} Videos remaining: '.format(len(files)-count_vids+1) + str(files[count_vids-1:])
               )
    
    # save data to file
    np.savetxt(basename + '.txt', np.column_stack((time_s, frame_nr, coord_x, coord_y)), delimiter=";", fmt='%s', header = head)


cv2.destroyAllWindows()