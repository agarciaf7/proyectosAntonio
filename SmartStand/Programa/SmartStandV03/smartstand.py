# -*- coding: cp1252 -*-
# Proyecto smartstand en mi Evernote
# Basado en de https://realpython.com/blog/python/face-recognition-with-python/
# y modificado con https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/
# para poder usarlo con la picamera o con una webcam normal
# Para mover el servo me baso en http://www.instructables.com/id/Servo-Motor-Control-With-Raspberry-Pi/
# Para detectar el movimiento en la imagen me baso en https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
# USAGE
# python smartstand.py --video face_tracking_example.mp4
# python smartstand.py --picamera 1 si es con picamera
# python smartstand.py si es con una webcam normal
# puede anadirse el parametro min-area para indicar el minimo area en el que se debe detectar movimiento

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from imutils.video import VideoStream
import time
import RPi.GPIO as GPIO

IMAGE_PORTIONS = 6 # Porciones horizontales en las que dividimos la deteccion en la imagen
MAX_ROTATION_ANGLE = 100 # Maximo angulo de rotacion que girara el soporte.

previousAngle = 1000 # Guardamos el angulo anterior

# initialize the first frame in the video stream
firstFrame = None

# Funcion para calcular el angulo al que hay que poner el soporte en funcion de la
# posicion horizontal del rostro en la imagen
def getAngle(image_width, image_portions, max_rotation_angle, horizontal_position):
        # ancho de cada porcion horizontal en la que dividimos la imagen
        portion_width = image_width / image_portions
        # porcion de la imagen, empezando por cero en la que esta el objeto
        portion = int(horizontal_position / portion_width)
        # grados de cada porcion del servo
        portion_angle = (max_rotation_angle / image_portions)
        # El resultado es el angulo correspondiente al centro de la porciÃ³n del servo con la que se corresponde en funcion de la porcion en la imagen
        result = (portion_angle * portion) + (portion_angle / 2)

        return result

# Funcion para calcular el angulo al que hay que poner el soporte en funcion de la
# posicion horizontal del rostro en la imagen
def getAngleSinPorciones(image_width, max_rotation_angle, horizontal_position):
        result = (horizontal_position * max_rotation_angle) / image_width
        return result

# Funcion para mover el servo en funcion del angulo que se le pase
def moveServo(angle, previousAngle):
        print ("previousAngle=", previousAngle)
        print ("moveServo angle=", angle)
        if angle != previousAngle :
        # if 1 == 1 :
            duty = angle / 18 + 2
            print ("Muevo servo")
            # Hago la inicializacion y parada cada vez en vez de hacerla unicamente al principio
            # para evitar que haga ruido constante
            pwm=GPIO.PWM(03, 50) # setup PWM on pin #3 at 50Hz
            pwm.start(0)
            
            pwm.ChangeDutyCycle(duty)
            time.sleep(0.2)
            
            pwm.stop()


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
ap.add_argument("-p", "--picamera", type=int, default=-1,
        help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-a", "--min-area", type=int, default=500,
        help="minimum area size")
ap.add_argument("-m", "--max-area", type=int, default=95000,
        help="maximum area size")
args = vars(ap.parse_args())

##cascPath = "./cascades/haarcascade_frontalface_alt.xml"

# Create the haar cascade
##faceCascade = cv2.CascadeClassifier(cascPath)

camera = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)

# Inicializamos el servo
GPIO.setmode(GPIO.BOARD)
GPIO.setup(03, GPIO.OUT)
#pwm=GPIO.PWM(03, 50) # setup PWM on pin #3 at 50Hz
#pwm.start(0)
##print ("Inicializacion a cero=", 0)
##moveServo(0, 500)
##time.sleep(5.0)
##print ("Inicializacion max=", MAX_ROTATION_ANGLE)
##moveServo(MAX_ROTATION_ANGLE, 500)
##time.sleep(5.0)
##print ("Inicializacion centro=", MAX_ROTATION_ANGLE/2)
##moveServo(MAX_ROTATION_ANGLE/2, 500)
##time.sleep(5.0)
##print ("Fin inicializacion")

# keep looping
while True:
        # grab the current frame
        image = camera.read()

        # resize the image, blur it, and convert it to the HSV
        # color space
        image = imutils.resize(image, width=600)

        # Le damos la vuelta (efecto espejo)
        image=cv2.flip(image,1)
##
        # convert the frame to grayscale, and blur it
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
##	(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        biggestContour = None #Guardaremos el mayor contorno
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"] or cv2.contourArea(c) > args["max_area"]:
			continue

		# Si llegamos aquÃ­ es que se ha detectado algun contorno con movimiento
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		# print("Contornos con movimiento: {0}".format(len(cnts)))
		if biggestContour is None or cv2.contourArea(c) > cv2.contourArea(biggestContour):
                        # si el nuevo contorno es mayor que el guardado lo sustituimos
                        biggestContour = c

        if biggestContour is not None:
            # Dibuja un circulo en el centro del mayor contorno
            (x, y, w, h) = cv2.boundingRect(biggestContour)
            cv2.circle(image, (x+(w/2), y+(h/2)), 15, (0, 255, 0), thickness=1, lineType=8, shift=0)
            print("Mayor area: {0}".format(cv2.contourArea(biggestContour)))
            print("Mover servo")
            # Tamano de la imagen
            image_height, image_width = image.shape[:2]
            #angle = getAngle(image_width, IMAGE_PORTIONS, MAX_ROTATION_ANGLE, (x+(w/2)))
            angle = getAngleSinPorciones(image_width, MAX_ROTATION_ANGLE, (x+(w/2)))
            #print angle
            moveServo(angle, previousAngle)
            previousAngle = angle







        # Detect faces in the image 
        # Para OPECV 3 (tambien sirve para 2.7)
##        faces = faceCascade.detectMultiScale(
##            gray,
##            scaleFactor=1.1,
##            minNeighbors=5,
##            minSize=(30, 30)
##            #flags = cv2.CV_HAAR_SCALE_IMAGE            
##        )
        # Tamano de la imagen
##        image_height, image_width = image.shape[:2]
        #print("width=", image_width, " height=", image_height)
        #print("Found {0} faces!".format(len(faces)))
        #print("Numero de caras=", len(faces))

        # Draw a rectangle around the faces
##        for (x, y, w, h) in faces:
##            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
##            # Dibuja un circulo en el centro del rectangulo
##            #cv2.circle(image, (x+(w/2), y+(h/2)), 15, (0, 255, 0), thickness=1, lineType=8, shift=0)
##            if len(faces) == 1 :
##                # Movemos el serv unicamente si hay una sola cara
##                #print("Mover servo")
##                angle = getAngle(image_width, IMAGE_PORTIONS, MAX_ROTATION_ANGLE, (x+(w/2)))
##                # angle = getAngleSinPorciones(image_width, MAX_ROTATION_ANGLE, (x+(w/2)))
##                #print angle
##                moveServo(angle, previousAngle)
##                previousAngle = angle

        # show the image to our screen
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
                break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

# Detenemos el servo
#pwm.stop()
GPIO.cleanup()



