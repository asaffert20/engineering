
import RPi.GPIO as GPIO
import RoboPiLib_pwm as RPL
import threading
from time import sleep
from ArmControl import Motor
from ArmControl import Encoder
RPL.RoboPiInit("/dev/ttyAMA0", 115200)

LockRotary = threading.Lock()		# create lock for rotary switch?


class Encoder(object, Enc_A, Enc_B):
    global LockRotary

    def __init__(self):
        self.Enc_A = Enc_A  # GPIO encoder pin A
        self.Enc_B = Enc_B  # GPIO encoder pin B
        self.Current_A = 1  # This assumes that Encoder inits while mtr is stop
        self.Current_B = 1
        self.Rotary_counter = 0
        self.startEncoders()

    def startEncoders(self):
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)					# Use BCM mode?
        # define the Encoder switch inputs ?
        GPIO.setup(self.Enc_A, GPIO.IN)
        GPIO.setup(self.Enc_B, GPIO.IN)
        # setup callback thread for the A and B encoder
        # use interrupts for all inputs
        GPIO.add_event_detect(self.Enc_A, GPIO.RISING,
                              callback=self.rotary_interrupt) 	# NO bouncetime
        GPIO.add_event_detect(self.Enc_B, GPIO.RISING,
                              callback=self.rotary_interrupt) 	# NO bouncetime
        return

    def rotary_interrupt(self, A_or_B):
        # read both of the switches
        Switch_A = GPIO.input(self.Enc_A)
        Switch_B = GPIO.input(self.Enc_B)
        # now check if state of A or B has changed
        # if not that means that bouncing caused it
        # Same interrupt as before (Bouncing)?
        if self.Current_A == Switch_A and self.Current_B == Switch_B:
            return										# ignore interrupt!

        self.Current_A = Switch_A						# remember new state
        Current_B = Switch_B							# for next bouncing check
        self.Current_B = Switch_B

        if (Switch_A and Switch_B):		# Both one active? Yes -> end of sequence
            LockRotary.acquire()		# get lock
            if A_or_B == self.Enc_B:		# Turning direction depends on
                self.Rotary_counter += 1		# which input gave last interrupt
            else:								# so depending on direction either
                self.Rotary_counter -= 1		# increase or decrease counter
            LockRotary.release()				# and release lock
        return									# THAT'S IT

###############################
    # Motor Class
###############################


class Motor(object):
    global freq

    def __init__(self):
        self.motor_number = 0
        self.controlPin = 0
        self.encoderPowerPin = 0
        self.ChannelA = 0
        self.ChannelB = 0
        self.forward_speed = 1000
        self.backward_speed = 1000
        self.encoder = 0
        self.cycleEvents = 0

    def stop(self):
        RPL.pwmWrite(self.controlPin, 1500, freq)

    def forwards(self):
        RPL.pwmWrite(self.controlPin, 1500 + speed, freq)

    def backwards(self):
        RPL.pwmWrite(self.controlPin, 1500 - speed, freq)

    def current_angle(self):
        angle = self.encoder.Rotary_counter / self.cycleEvents
        angle = angle * 360
        return angle

    def move_to_position(self, new_position):
        if new_position > self.encoder.Rotary_counter:
            self.forwards()
        if new_position < self.encoder.Rotary_counter:
            self.backwards()
        else:
            self.stop()
