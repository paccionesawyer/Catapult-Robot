import adafruit_pca9685
from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels = 16)
engager = kit.servo[1]
catapult = kit.servo[0]

CatapultStartAngle = 5
EngageStartAngle = 0

CatapultEndAngle = 100
EngageEndAngle = 90

# def engag
# catapult.angle = CatapultEndAngle
time.sleep(1)
engager.angle = EngageEndAngle

def engageMotor():
    catapult.angle = CatapultStartAngle
    time.sleep(1)
    engager.angle = EngageStartAngle
    time.sleep(1)
    # catapult.angle = CatapultEndAngle

def releaseMotor():
    engager.angle = EngageEndAngle

engageMotor()
time.sleep(3)
# releaseMotor()