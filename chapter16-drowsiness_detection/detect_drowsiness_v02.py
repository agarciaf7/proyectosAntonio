# USAGE
# python detect_drowsiness.py --conf config/config.json

# import the necessary packages
from pyimagesearch.utils import Conf
from imutils.video import VideoStream
from imutils import face_utils
from datetime import datetime
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

def euclidean_dist(ptA, ptB):
    # compute and return the euclidean distance between the two
    # points
    return np.linalg.norm(ptA - ptB)

def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    a = euclidean_dist(eye[1], eye[5])
    b = euclidean_dist(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    c = euclidean_dist(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (a + b) / (2.0 * c)

#    print('eye=' + str(eye) +' eye[0]=' + str(eye[0]) + ' eye[3]=' + str(eye[3]))
    
#    cv2.circle(frame, (eye[0][0], eye[0][1]), 10, (255, 0, 0), 2) #prueba

    # return the eye aspect ratio
    return ear

def mouth_aspect_ratio(mouth):
    # compute the euclidean distances between the three sets of
    # vertical mouth landmarks (x, y)-coordinates
    a = euclidean_dist(mouth[1], mouth[7])
    b = euclidean_dist(mouth[2], mouth[6])
    c = euclidean_dist(mouth[3], mouth[5])

    # compute the euclidean distance between the horizontal
    # mouth landmark (x, y)-coordinates
    d = euclidean_dist(mouth[0], mouth[4])

    # compute the mouth aspect ratio
    mar = (a + b + c) / (2.0 * d)

    # return the mouth aspect ratio
    return mar

# Calcula la desviación de la nariz respecto a los ojos
def nose_desviation(leftEye, rightEye, nose):
    desviation = 0
    #Sólo usaremos la coordenada x (columnas) de los ojos y la nariz
    x_extremo_leftEye = leftEye[3][0] #extremo izqdo del ojo izqdo
    x_extremo_rightEye = rightEye[0][0] #extremo dcho del ojo dcho
    x_centro_nose = nose[2][0]
#    print('x_extremo_leftEye='+str(x_extremo_leftEye)+' x_extremo_rightEye='+str(x_extremo_rightEye)+' x_centro_nose='+str(x_centro_nose))
    
    centro_entre_ojos = x_extremo_rightEye + ((x_extremo_leftEye - x_extremo_rightEye) / 2)
    
    desviation = x_centro_nose - centro_entre_ojos # Negativo es que está girado a la izqda
#    print('centro_entre_ojos='+str(centro_entre_ojos) + ' desviation=' + str(desviation))

    return desviation

def check_closed_eyes(shape, lStart, lEnd, rStart, rEnd, cv2, frame):

    global blinkCounter, alarmOn, th
    
    # extract the left and right eye coordinates
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    # we use eyes
    # coordinates to compute the eye aspect ratio for both eyes
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    # average the eye aspect ratio together for both eyes
    ear = (leftEAR + rightEAR) / 2.0

    # compute the convex hull for the left and right eye, then
    # visualize each of the eyes
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

    if ear < conf["EYE_AR_THRESH"]:
        # increment the blink frame counter
        blinkCounter += 1

        # if the eyes were closed for a sufficient number of
        # frames, then sound the alarm
        if blinkCounter >= conf["EYE_AR_CONSEC_FRAMES"]:
            # if the alarm is not on, turn it on
            if not alarmOn:
                alarmOn = True

                # check to see if the TrafficHat buzzer should
                # be sounded and red light set to blink
                if conf["alarm"]:
                    th.buzzer.blink(0.1, 0.1, 5,
                        background=True)
                    th.lights.red.blink(0.1, 0.1, 10,
                        background=True)

            # draw an alarm on the frame
            cv2.putText(frame, "ALERTA! - ojos cerrados", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # otherwise, the eye aspect ratio is not below the blink
    # threshold, so reset the counter and alarm
    else:
        blinkCounter = 0
        alarmOn = False
        
    return
    
def check_yawn(shape, mStart, mEnd, cv2, frame):

    global yawnCounter, alarmOn, th, startTime    
    # extract the inner mouth coordinates, then use the
    # coordinates to compute the mouth aspect ratio for the mouth
    mouth = shape[mStart:mEnd]
    mar = mouth_aspect_ratio(mouth)

    # compute the convex hull for the mouth then
    # visualize the mouth
    mouthHull = cv2.convexHull(mouth)
    cv2.drawContours(frame, [mouthHull], -1, (0, 0, 255), 1)
    
    # check to see if the mouth aspect ratio is above the yawn
    # threshold
    if mar > conf["MOUTH_AR_THRESH"]:
        # increment the yawn frame counter and set the start time
        yawnCounter += 1
        startTime = datetime.now() if startTime == None else \
            startTime

        # check to see if yawn frame counter is greater than yawn
        # frame threshold and if the difference between current
        # time and start time is less than or equal to yawn
        # threshold time (in which case the person is drowsy)           
        if yawnCounter >= conf["YAWN_THRESH_COUNT"] and \
            (datetime.now() - startTime).seconds <= \
            conf["YAWN_THRESH_TIME"]:
            # if the alarm is not on, turn it on
            if not alarmOn:
                alarmOn = True

                # check to see if the TrafficHat buzzer should
                # be sounded and red light set to blink
                if conf["alarm"]:
                    th.buzzer.blink(0.1, 0.1, 5,
                        background=True)
                    th.lights.yellow.blink(0.1, 0.1, 10,
                        background=True)

            # draw an alarm on the frame
            cv2.putText(frame, "ALERTA! - bostezo",
                (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 255), 2)

    # check to see if the start time is set
    elif startTime != None:
        # check if the difference between current time and start
        # time is greater than yawn threshold time
        if (datetime.now() - startTime).seconds > \
            conf["YAWN_THRESH_TIME"]:
            # reset yawn counter, alarm flag and start time
            yawnCounter = 0
            alarmOn = False
            startTime = None
    return

def check_head_turn(shape, mStart, mEnd, lStart, lEnd, rStart, rEnd, cv2, frame):

    global alarmOn, th, noseDesviationCounter
    # dibujamos la nariz
    nose = shape[nStart:nEnd]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    noseHull = cv2.convexHull(nose)
    cv2.drawContours(frame, [noseHull], -1, (0, 0, 255), 1)

    noseDesviation = nose_desviation(leftEye, rightEye, nose)
    
    if abs(noseDesviation) > conf["NOSE_AR_THRESH"]:
        # increment the nose frame counter
        noseDesviationCounter += 1

        # if the nose was turned for a sufficient number of
        # frames, then sound the alarm
        if noseDesviationCounter >= conf["NOSE_AR_CONSEC_FRAMES"]:
            # if the alarm is not on, turn it on
            if not alarmOn:
                alarmOn = True

                # check to see if the TrafficHat buzzer should
                # be sounded and red light set to blink
                if conf["alarm"]:
                    th.buzzer.blink(0.1, 0.1, 5,
                        background=True)
                    th.lights.green.blink(0.1, 0.1, 10,
                        background=True)

            # draw an alarm on the frame
            cv2.putText(frame, "ALERTA! - cabeza girada", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # otherwise, the eye aspect ratio is not below the blink
    # threshold, so reset the counter and alarm
    else:
        noseDesviationCounter = 0
        alarmOn = False    
    
    return

def draw_jaw(shape, jStart, jEnd, cv2, frame):
    # extract the jaw (mandibula) coordinates
    jaw = shape[jStart:jEnd]

    # compute the convex hull for the left and right eye, then
    # visualize each of the eyes
    jawHull = cv2.convexHull(jaw)
    cv2.drawContours(frame, [jawHull], -1, (0, 255, 0), 1)


# ****************************************************************
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
    help="Path to the input configuration file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# check to see if we are using GPIO/TrafficHat as an alarm
if conf["alarm"]:
    from gpiozero import TrafficHat
    th = TrafficHat()
    print("[INFO] using TrafficHat alarm...")

# initialize the frame center coordinates
centerX = None
centerY = None

# initialize the blink counter, yawn counter, noseDesviationCounter a boolean used to
# indicate if the alarm is going off, and start time
blinkCounter = 0
yawnCounter = 0
noseDesviationCounter = 0
alarmOn = False
startTime = None
pause = False

# load OpenCV's Haar cascade for face detection (which is faster than
# dlib's built-in HOG detector, but less accurate), then create the
# facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = cv2.CascadeClassifier(conf["cascade_path"])
predictor = dlib.shape_predictor(conf["shape_predictor_path"])

# grab the indexes of the facial landmarks for the left, right eye,
# and inner part of the mouth respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["inner_mouth"]
(nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]
(jStart, jEnd) = face_utils.FACIAL_LANDMARKS_IDXS["jaw"]


# start the video stream thread
print("[INFO] starting video stream thread...")

#    vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()

# Damos un tiempo para que se inicialice la cámara iluminando
# el traffic hat o si no está activo con un sleep
if conf["alarm"]:
    th.buzzer.blink(0.2, 0, 1, background=True)
    th.lights.green.blink(0.5, 0, 1, background=False)
    th.buzzer.blink(0.2, 0, 1, background=True)
    th.lights.yellow.blink(0.5, 0, 1, background=False)
    th.buzzer.blink(0.2, 0, 1, background=True)
    th.lights.red.blink(0.5, 0, 1, background=False)
else:
    time.sleep(2.0)
    

# loop over frames from the video stream
while True:
    
    if conf["alarm"]:
        # Controlamos el botón
        if (th.button.is_pressed):
            print ("Botón pulsado")
            if (pause):
                #Desactivamos la pausa
                pause = False
                th.buzzer.blink(0.5, 0.2, 2, background=True)
                th.lights.green.blink(0.5, 0.2, 2, background=True)
                time.sleep(1.0)
            else:
                #Activamos la pausa
                pause = True
                th.buzzer.blink(0.5, 0.2, 1, background=True)
                th.lights.red.blink(0.5, 0.2, 2, background=True)
                time.sleep(1.0)
                
    if (pause):
        continue #No hacemos nada más en el blucle

    # grab the frame from the threaded video file stream, resize,
    # flip horizontally, and convert to grayscale
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    # Como la cámara está invertida roto imagen sobre eje x
    frame = cv2.flip(frame, 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # set the frame center coordinates
    if centerX is None and centerY is None:
        (centerX, centerY) = (frame.shape[1] // 2,
            frame.shape[0] // 2)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
        minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)

    # loop over the detected faces
    for rect in rects:
        # draw a bounding box surrounding the face
        (x, y, w, h) = rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # check if the number of faces detected is greater than zero
    if len(rects) > 0:
        # sort the detected rectangles by their position relative to
        # the center and grab the face that's closest to the center
        centerRect = sorted(rects, key=lambda r: abs((
            r[0] + (r[2] / 2)) - centerX) + abs((
            r[1] + (r[3] / 2)) - centerY))[0]

        # get the coordinates of the rectangle in the center and
        # construct a dlib rectangle object from the Haar cascade
        # bounding box
        (x, y, w, h) = centerRect
        rect = dlib.rectangle(int(x), int(y), int(x + w),
            int(y + h))

        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        
#        print ('shape=' + str(shape))

        # extract the left and right eye coordinates
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]


        check_closed_eyes(shape, lStart, lEnd, rStart, rEnd, cv2, frame)
        check_yawn(shape, mStart, mEnd, cv2, frame)
        check_head_turn(shape, mStart, mEnd, lStart, lEnd, rStart, rEnd, cv2, frame)
        draw_jaw(shape, jStart, jEnd, cv2, frame)

    # if the 'display flag is set, then display the current frame
    # to the screen and record if a user presses a key
    if conf["display"]:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

# check to see if we have any open windows, and if so, close them
if conf["display"]:
    cv2.destroyAllWindows()

# release the video stream pointer
vs.stop()