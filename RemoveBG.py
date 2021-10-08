# -*- coding: utf-8 -*-
"""
remove static bakcground from a video
acquire background first with 'AccumulateBackground.py' and save as 'backg.jpg'
"""

import numpy as np
import cv2
import os

dir = 'C:\\Users\\xyz\\Videos'
os.chdir(dir)

fname = 'video.avi'
cap = cv2.VideoCapture(fname)
img = 'backg.jpg'
backg = cv2.imread(img,0)

cv2.namedWindow('output', cv2.WINDOW_NORMAL)
cv2.namedWindow('input', cv2.WINDOW_NORMAL)
cv2.namedWindow('contrast', cv2.WINDOW_NORMAL)

back_mean = (cv2.mean(backg)[0])
#kernel = np.ones((4,4))


while True:
    grabbed, frame = cap.read()
    key = cv2.waitKey(1) & 0xFF
    
    if not grabbed:
        print "Processing " + fname + " ended"
        break     
    
#### flatfield correction
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype('float64')  
    
    temp = cv2.divide(img_gray,backg.astype('float64'))    
    new_frame = back_mean * temp
#### correct brightness if necessary 
#    dilate = cv2.erode(new_frame.astype('uint8'), kernel)
    contrast = new_frame + 10
#### display raw and processed frames 
#    cv2.imshow('input',frame)
#    cv2.imshow('output',new_frame.astype('uint8'))
#    cv2.imshow('contrast', contrast.astype('uint8'))
##### save frames
    frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES) 
    filename = 'frame%i.jpg' %frame_nr
    print(filename)
    cv2.imwrite(filename,contrast)
    print frame_nr
####
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
####

cv2.destroyAllWindows()