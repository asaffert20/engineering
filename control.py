import RoboPiLib as RPL
RPL.RoboPiInit("/dev/ttyAMA0",115200)
import xbox
import math

import sys, tty, termios, signal

######################
## Motor Establishment
######################

motorL = 0
motorR = 1


try:
  RPL.pinMode(motorL,RPL.SERVO)
  RPL.servoWrite(motorL, 1500)
  RPL.pinMode(motorR,RPL.SERVO)
  RPL.servoWrite(motorR, 1500)
except:
  pass


######################
## Individual commands
######################
def stopAll():
  try:
    RPL.servoWrite(motorL,1500)
    RPL.servoWrite(motorR,1500)
  except:
    print "error except"
    pass

global sensitivity
sensitivity = 500


def rightMotorScaled(x, y):
        f = int(1250 * y)
        t = int(750 * x)
        scaled = f - t
        return int(min(1500 + scaled, 3000))


def leftMotorScaled(x, y):
        f = int(1250 * y)
        t = int(750 * x)
        scaled = f + t
        return int(max(1500 - scaled,0))



if __name__ == '__main__':
    joy = xbox.Joystick()
    global sensitivity

    while not joy.Back():

        # Servo
        x, y = joy.leftStick()

        RPL.servoWrite(motorL,leftMotorScaled(x, y))
        RPL.servoWrite(motorR,rightMotorScaled(x, y))

        if joy.A() == 1:
                sensitivity += 10
                print sensitivity
        if joy.B() == 1:
                sensitivity -= 10
                print sensitivity


joy.close()
stopAll()
