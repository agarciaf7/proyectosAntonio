# Para mover el servo me baso en http://www.instructables.com/id/Servo-Motor-Control-With-Raspberry-Pi/
# USAGE
# python pruebaservo.py 
# import the necessary packages
import cv2
import time
import RPi.GPIO as GPIO

# Funcion para mover el servo en funcion del angulo que se le pase
def moveServo(angle):
        duty = angle / 18 + 2
        GPIO.output(03, True)
        pwm.ChangeDutyCycle(duty)
        time.sleep(3.0)
        GPIO.output(03, False)
        pwm.ChangeDutyCycle(0)

# Inicializamos el servo
GPIO.setmode(GPIO.BOARD)
GPIO.setup(03, GPIO.OUT)
pwm=GPIO.PWM(03, 50) # setup PWM on pin #3 at 50Hz
pwm.start(0)
print "moveServo(90)"
moveServo(90)
print "moveServo(20)"
moveServo(20)
print "moveServo(160)"
moveServo(160)


# Detenemos el servo
pwm.stop()
GPIO.cleanup()



