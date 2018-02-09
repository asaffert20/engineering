################################
# ArmControlLib v0.1
#
# Copyright Jack Rickman, 2018
#
# Designed to control Brushed DC motors with encoders
#
# Designed for Benilde St. Margaret's Rescue Robot, running on
# Raspberry Pi 3's with RoboPi hats.
#
# Utilizes the RoboPiLib library (RoboPyLib_pwmv0_97.py), from William Henning
#
##################################
import threading
import time
import RPi.GPIO as GPIO
import RoboPiLib_pwm as RPL
LockRotary = threading.Lock()

###############################
# Encoder Class
###############################


class Encoder(object):
    global LockRotary

    def __init__(self, Enc_A, Enc_B):
        self.Enc_A = Enc_A  # GPIO encoder pin A
        self.Enc_B = Enc_B  # GPIO encoder pin B
        self.Current_A = 1  # This assumes that Encoder inits while mtr is stopped
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

    def __init__(self, controlPin, encoderPowerPin, Enc_A, Enc_B,
                 forward_speed, backward_speed, cycleEvents, freq):
        self.controlPin = controlPin
        self.encoder = Encoder(Enc_A, Enc_B)
        self.forward_speed = forward_speed
        self.backward_speed = backward_speed
        self.cycleEvents = cycleEvents
        self.freq = freq
        self.encoderPowerPin = encoderPowerPin
        self.pinSetup()

    def pinSetup(self):
        RPL.pinMode(self.encoderPowerPin, RPL.OUTPUT)
        RPL.digitalWrite(encoderPowerPin, 1)
        RPL.pinMode(self.controlPin, RPL.PWM)

    def stop(self):
        RPL.pwmWrite(self.controlPin, 1500, self.freq)

    def forwards(self):
        RPL.pwmWrite(self.controlPin, 1500 + self.forward_speed, self.freq)

    def backwards(self):
        RPL.pwmWrite(self.controlPin, 1500 - self.backward_speed, self.freq)

    def current_angle(self):
        angle = self.encoder.Rotary_counter / self.cycleEvents
        angle = angle * 360
        return angle

    def move_to_position(self, new_position):
        if new_position > self.encoder.Rotary_counter:
            self.forwards()
            print "Motor forwards"
        if new_position < self.encoder.Rotary_counter:
            self.backwards()
            print "Motor backwards"
        else:
            self.stop()

############################
    # Inverse Kinimatics
############################
