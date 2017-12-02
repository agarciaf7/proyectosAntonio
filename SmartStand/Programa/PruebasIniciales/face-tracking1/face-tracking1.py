# Tomado de https://realpython.com/blog/python/face-recognition-with-python/
# y modificado con https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/
# para poder usarlo con la picamera o con una webcam normal
# USAGE
# python face-tracking1.py --video face_tracking_example.mp4
# python face-tracking1.py --picamera 1 si es con picamera
# python face-tracking1.py si es con una webcam normal

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from imutils.video import VideoStream
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())

cascPath = "./cascades/haarcascade_frontalface_alt.xml"

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

camera = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)


# keep looping
while True:
	# grab the current frame
	image = camera.read()

	# resize the image, blur it, and convert it to the HSV
	# color space
	#image = imutils.resize(image, width=600)

	# Le damos la vuelta (efecto espejo)
	#image=cv2.flip(image,1)
	
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image 
        # Para OPECV 3 (tambien sirve para 2.7)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            #flags = cv2.CV_HAAR_SCALE_IMAGE            
        )

        print("Found {0} faces!".format(len(faces)))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)


	# show the image to our screen
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
