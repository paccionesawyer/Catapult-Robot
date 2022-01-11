from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from faceControl.objcenter import ObjCenter
from faceControl.pid import PID
from speechR import SpeechRecognizer

import argparse
import signal
import time
import sys
import cv2
import adafruit_pca9685
from adafruit_servokit import ServoKit

# Import Servo controller
kit = ServoKit(channels = 16)
baseMotor = kit.servo[3]
baseMotor.angle = 90
minAngle = 0
maxAngle = 180
engageAngle = 160
# set limits of

# function to handle keyboard interrupt


def signal_handler(sig, frame):
    # print a status message
    print("[INFO] You pressed `ctrl + c`! Exiting...")

    # disable the servos

    # exit
    sys.exit()


def obj_center(args, objX, centerX):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    # start the video stream and wait for the camera to warm up
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    # initialize the object center finder
    obj = ObjCenter(args["cascade"])

    # loop indefinitely
    while True:
        # grab the frame from the threaded video stream and flip it
        # vertically (since our camera was upside down)
        frame = vs.read()

        # calculate the center of the frame as this is where we will
        # try to keep the object
        (H, W) = frame.shape[:2]
        centerX.value = W // 2

        # find the object's location
        objectLoc = obj.update(frame, (centerX.value))
        ((objX.value), rect) = objectLoc

        if (type(objX.value) == "<class 'tuple'>"):
            objX.value = objX.value[0]

        # extract the bounding box and draw it
        if rect is not None:
            (x, y, w, h) = rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
                2)

        # display the frame to the screen
        cv2.imshow("Pan-Tilt Face Tracking", frame)
        cv2.waitKey(1)


# loop 
def pid_process(output, p, i, d, objCoord, centerCoord): 
    # signal trap to handle keyboard interrupt 
    signal.signal(signal.SIGINT, signal_handler) 
    
    # create a PID and initialize it 
    # TODO Possible error with multiple p
    p = PID(p.value, i.value, d.value) 
    p.initialize() 
    
    # loop indefinitely 
    while True: 
        # calculate the error 
        if (type(objCoord.value) == tuple):
            objCoord.value = objCoord.value[0]
        error = centerCoord.value - objCoord.value 
        output.value = p.update(error)
        # indefinitely 
        while True: 
            # calculate the error 
            # print("Center:", type(centerCoord.value))
            # print("objCenter:", type(objCoord.value))
            if (type(objCoord.value) == tuple):
                objCoord.value = objCoord.value[0]
            error = centerCoord.value - objCoord.value 
            print("error", error)
            output.value = p.update(error)

def check_speech(throw):
    signal.signal(signal.SIGINT, signal_handler) 

    listener = SpeechRecognizer()

    # loop indefinitely 
    while True: 
        response = listener.recognize_speech_from_mic()
        print("Response:", response)
        if response == 'ball':
            throw.value = 1
        


def in_range(val, start, end):
    # determine the input value is in the supplied range
    return (val >= start and val <= end)

def set_servo(pan): 
    # signal trap to handle keyboard interrupt 
    signal.signal(signal.SIGINT, signal_handler) # loop indefinitely 
    while True: 
        panAngle = pan.value
        # print(panAngle)
        # if the pan angle is within the range, pan 
        if in_range(panAngle, -90, 90): 
            panAngle = panAngle + 90
            baseMotor.angle = panAngle
            

# check to see if this is the main body of execution
if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cascade", type=str, required=True,
        help="path to input Haar cascade for face detection")
    args = vars(ap.parse_args())

    # start a manager for managing process-safe variables
    with Manager() as manager:
        # enable the servos

        # set integer values for the object center (x)-coordinates
        centerX = manager.Value("i", 0)

        # set integer values for the object's (x)-coordinates
        objX = manager.Value("i", 0)

        # pan and tilt values will be managed by independent PIDs
        pan = manager.Value("i", 90)

        # set PID values for panning
        panP = manager.Value("f", 0.2)
        panI = manager.Value("f", 0.00)
        panD = manager.Value("f", 0.000)

        throw = manager.Value("i", 0)

        # we have 4 independent processes
        # 1. objectCenter  - finds/localizes the object
        # 2. panning       - PID control loop determines panning angle
        # 3. tilting       - PID control loop determines tilting angle
        # 4. setServos     - drives the servos to proper angles based
        #                    on PID feedback to keep object in center
        processObjectCenter = Process(target=obj_center,
            args=(args, objX, centerX))
        processPanning = Process(target=pid_process,
            args=(pan, panP, panI, panD, objX, centerX))
        processSetServos = Process(target=set_servo, args=(pan,))
        processCheckSpeech = Process(target=check_speech, args =(throw,))

        # start all 4 processes
        processObjectCenter.start()
        processPanning.start()
        processSetServos.start()
        # processCheckSpeech.start()

        # join all 4 processes
        processObjectCenter.join()
        processPanning.join()
        processSetServos.join()
        # processCheckSpeech.join()

        # disable the servos