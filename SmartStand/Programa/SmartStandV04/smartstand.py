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
from pyimagesearch.shapedetector import ShapeDetector
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
        # load the image and resize it to a smaller factor so that
        # the shapes can be approximated better
        resized = imutils.resize(image, width=300)
        ratio = image.shape[0] / float(resized.shape[0])
         
        # convert the resized image to grayscale, blur it slightly,
        # and threshold it
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
         
        # find contours in the thresholded image and initialize the
        # shape detector
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector()

        # loop over the contours
        for c in cnts:
                # compute the center of the contour, then detect the name of the
                # shape using only the contour
                M = cv2.moments(c)
                cX = int((M["m10"] / (M["m00"] + 1e-7)) * ratio)
                cY = int((M["m01"] / (M["m00"] + 1e-7)) * ratio)
                shape = sd.detect(c)
         
                # multiply the contour (x, y)-coordinates by the resize ratio,
                # then draw the contours and the name of the shape on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
         
        






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



