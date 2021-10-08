"""
run once to accumulate background, i.e. non-moving objects
uncomment imwrite in Line 60 to save background as backg.jpg
"""

import numpy as np
import cv2
import os
from PIL import Image


dir = 'C:\\Users\\xyz\\Videos'
os.chdir(dir)

fname = 'video.avi'

cap = cv2.VideoCapture(fname)

_, firstframe = cap.read()
gray = cv2.cvtColor(firstframe, cv2.COLOR_BGR2GRAY)
avg = np.float64(gray)


cv2.namedWindow('backg', cv2.WINDOW_NORMAL)


while True:
    grabbed, frame = cap.read()
    key = cv2.waitKey(1) & 0xFF
    
    frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
    print frame_nr
    
    if not grabbed:
        print "Processing " + fname + " ended"
        break
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype('float64')  
    cv2.accumulate(img_gray,avg)
        

    backg = avg/frame_nr
  
    cv2.imshow('backg',backg.astype('uint8'))
    im = Image.fromarray(backg)
    filename = 'background%i.tif' %frame_nr
    im.save(filename)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


#cv2.imwrite('backg.jpg',backg)
cv2.destroyAllWindows()