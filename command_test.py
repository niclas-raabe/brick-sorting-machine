import ev3_dc as ev3
import threading
import signal
import sys
from time import sleep
import requests
import cv2
import logging

# setup logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

# setup camera
logging.debug('Setup camera')
cap = cv2.VideoCapture(0)
sleep(2)

# setup motors and sensors
logging.debug('Setup motors and sensors')
motor = ev3.Motor(ev3.PORT_A, protocol=ev3.USB)
motor2 = ev3.Motor(ev3.PORT_B, ev3_obj=motor)
motor3 = ev3.Motor(ev3.PORT_C, ev3_obj=motor)
motor4 = ev3.Motor(ev3.PORT_D, ev3_obj=motor, speed=100, verbosity=2)
sensorColorCamera = ev3.Color(ev3.PORT_4, ev3_obj=motor)
sensorBuckets = ev3.Color(ev3.PORT_3, ev3_obj=motor)

motor.speed = 75
motor2.speed = 10
motor3.speed = 20


def startAllMotors():
    motor2.start_move(direction=-1)
    motor3.start_move(direction=-1)
    motor4.start_move(direction=-1)


def stopAllMotors():
    motor.stop()
    motor2.stop()
    motor3.stop()
    motor4.stop()


def printSensors():
    colorCameraAmbient = sensorColorCamera.ambient
    logging.debug(f'colorCameraAmbient: {colorCameraAmbient}')
    sensorBucketsAmbient = sensorBuckets.ambient
    logging.debug(f'sensorBucketsAmbient: {sensorBucketsAmbient}')


def checkIncomingPart():
    if sensorColorCamera.ambient < 45:
        while sensorColorCamera.ambient < 45:
            logging.debug('wait for part is complete on belt')
        stopMotorsForPartCheck()

        # wait for recognotion
        sleep(1)
        takePhoto()
        recognizePart()

        rotateBucketToNextSlot()

        startMotorsAfterPartCheck()
    else:
        logging.debug(f'No part on camera sensor {sensorColorCamera.ambient}')


def stopMotorsForPartCheck():
    motor2.stop()
    motor3.stop()
    motor4.stop()


def startMotorsAfterPartCheck():
    motor3.start_move()

    # wait until the part left the belt
    sleep(5)

    motor2.start_move(direction=-1)
    motor4.start_move(direction=-1)


def rotateBucketToNextSlot():
    logging.debug(f'rotateBucketToNextSlot')
    motor.start_move(direction=-1)
    sleep(0.1)
    logging.debug(f'sensorBuckets.reflected at start: {sensorBuckets.reflected}')
    while sensorBuckets.reflected < 22:
        logging.debug(
            f'wait for bucket to be rotated completely: {sensorBuckets.reflected}')
    logging.debug(f'sensorBuckets.reflected at end: {sensorBuckets.reflected}')
    motor.stop()


def recognizePart():
    multipart_form_data = {
        'query_image': ('capture.png', open('capture.jpg', 'rb'), 'image/jpeg')
    }
    response = requests.post(
        'https://api.brickognize.com/predict/parts/', files=multipart_form_data)
    logging.debug(response.content)


def takePhoto():
	ret, frame = cap.read()
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	cv2.imwrite('capture.jpg', frame)

running = True
def run():
    global running
    startAllMotors()
    while running:
        printSensors()
        checkIncomingPart()
    stopAllMotors()


def stop():
    global running
    running = False
    stopAllMotors()
    cap.release()


t = threading.Thread(target=run)
t.start()


def signal_handler(sig, frame):
    logging.debug('You pressed Ctrl+C!')
    stopAllMotors()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
logging.debug('Press Ctrl+C')
signal.pause()
