# Tomado de https://realpython.com/blog/python/face-recognition-with-python/
# y modificado con https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/
# para poder usarlo con la picamera o con una webcam normal
# Pinta el centro de los rectangulos de las caras
# USAGE
# python smartstand.py --video face_tracking_example.mp4
# python smartstand.py --picamera 1 si es con picamera
# python smartstand.py si es con una webcam normal

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from imutils.video import VideoStream
import time

IMAGE_PORTIONS = 6 # Porciones horizontales en las que dividimos la deteccion en la imagen
MAX_ROTATION_ANGLE = 180 # Maximo angulo de rotacion que girara el soporte

# Funcion para calcular el angulo al que hay que poner el soporte en funcion de la
# posicion horizontal del rostro en la imagen
def angle(image_width, image_portions, max_rotation_angle, horizontal_position):
        # ancho de cada porcion horizontal en la que dividimos la imagen
        portion_width = image_width / image_portions
        # porcion, empezando por cero en la que esta el objeto
        portion = int(horizontal_position / portion_width)
        portion_angle = (max_rotation_angle / image_portions)

        if horizontal_position <= (image_width / 2) :
                result = (portion + 1) * portion_angle
        else :
                result = portion * portion_angle

        return result


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
        # Tamano de la imagen
        image_height, image_width = image.shape[:2]
        #print("width=", image_width, " height=", image_height)
        #print("Found {0} faces!".format(len(faces)))
        #print("Numero de caras=", len(faces))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Dibuja un circulo en el centro del rectangulo
            #cv2.circle(image, (x+(w/2), y+(h/2)), 15, (0, 255, 0), thickness=1, lineType=8, shift=0)
            print angle(image_width, IMAGE_PORTIONS, MAX_ROTATION_ANGLE, (x+(w/2)))

        if len(faces) == 1 :
                # Movemos el soporte unicamente si hay una sola cara
                print("Mover soporte")
                #moveStand #TODO

	# show the image to our screen
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()


