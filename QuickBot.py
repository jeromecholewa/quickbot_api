#!/usr/bin/python
"""
@brief QuickBot class for Beaglebone Black

@author Rowland O'Flaherty (rowlandoflaherty.com)
@date 02/07/2014
@version: 1.0
@copyright: Copyright (C) 2014, Georgia Tech Research Corporation
see the LICENSE file included with this software (see LINENSE file)
"""

from __future__ import division
import sys
import time
import re
import socket
import threading
import numpy as np
import config
import beaglebone_pru_adc as adc

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

# Constants
LEFT = 0
RIGHT = 1
MIN = 0
MAX = 1

DEBUG = False

ADCTIME = 0.001

## Tic toc constants
TICTOC_START = 0
TICTOC_COUNT = 0
TICTOC_MEAN = 0
TICTOC_MAX = -float('inf')
TICTOC_MIN = float('inf')

class QuickBot():
    """The QuickBot Class"""

    # === Class Properties ===
    # Parameters
    sampleTime = 20.0 / 1000.0

    # Pins
    ledPin = 'USR1'

    # Motor Pins -- (LEFT, RIGHT)
    dir1Pin = (config.MOTOR_LEFT['dir1'], config.MOTOR_RIGHT['dir1'])
    dir2Pin = (config.MOTOR_LEFT['dir2'], config.MOTOR_RIGHT['dir2'])
    pwmPin = (config.MOTOR_LEFT['pwm'], config.MOTOR_RIGHT['pwm'])

    # ADC Pins
    irPin = config.IR_PINS
    encoderPin = ( 0, 2 )  # AIN0, AIN2

    # Encoder counting parameter and variables
    ticksPerTurn = 16  # Number of ticks on encoder disc
    encWinSize = 2**5  # Should be power of 2
    minPWMThreshold = [45, 45]  # Threshold on the minimum value to turn wheel
    encTPrev = [0.0, 0.0]
    encThreshold = [0.0, 0.0]
    encTickState = [0, 0]
    encTickStateVec = np.zeros((2, encWinSize))

    # Constraints
    pwmLimits = [-100, 100]  # [min, max]

    # State PWM -- (LEFT, RIGHT)
    pwm = [0, 0]

    # State IR
    irVal = [0.0, 0.0, 0.0, 0.0, 0.0]
    ithIR = 0

    # State Encoder
    encTime = [0.0, 0.0]  # Last time encoders were read
    encPos = [0.0, 0.0]  # Last encoder tick position
    encVel = [0.0, 0.0]  # Last encoder tick velocity

    # Encoder counting parameters
    encCnt = 0  # Count of number times encoders have been read
    encSumN = [0, 0]  # Sum of total encoder samples

    ## Stats of encoder values while input = 0 and vel = 0
    encZeroCntMin = 2**4  # Min number of recorded values to start calculating stats
    encZeroMean = [0.0, 0.0]
    encZeroVar = [0.0, 0.0]
    encZeroCnt = [0, 0]
    encHighCnt = [0, 0]
    encLowCnt = [0, 0]
    encLowCntMin = 2

    # Variables
    ledFlag = True
    cmdBuffer = ''

    # UDP
    port = config.PORT
    robotSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    robotSocket.settimeout(0.005)

    # === Class Methods ===
    # Constructor
    def __init__(self, baseIP, robotIP):

        # Initialize GPIO pins
        GPIO.setup(self.dir1Pin[LEFT], GPIO.OUT)
        GPIO.setup(self.dir2Pin[LEFT], GPIO.OUT)
        GPIO.setup(self.dir1Pin[RIGHT], GPIO.OUT)
        GPIO.setup(self.dir2Pin[RIGHT], GPIO.OUT)

        GPIO.setup(self.ledPin, GPIO.OUT)

        # Initialize PWM pins: PWM.start(channel, duty, freq=2000, polarity=0)
        PWM.start(self.pwmPin[LEFT], 0)
        PWM.start(self.pwmPin[RIGHT], 0)


        # Initialize ADC
        self._adc = adc.Capture()
        self._adc.encoder0_pin = self.encoderPin[0]
        self._adc.encoder1_pin = self.encoderPin[1]
        self._adc.encoder0_threshold = config.MOTOR_LEFT['threshold']
        self._adc.encoder1_threshold = config.MOTOR_RIGHT['threshold']
        self._adc.encoder0_delay = 200
        self._adc.encoder1_delay = 200

        # Set IP addresses
        self.baseIP = baseIP
        self.robotIP = robotIP
        self.robotSocket.bind((self.robotIP, self.port))

        self._last_ticks = (0, 0)  # remember last tick reading (to compute delta)
        self._pwm_ema = [0, 0]  # models actual (inertial) speed by EMA-averaging pwm
        self._ema_period = config.PWM_EMA_PERIOD  # EMA-averaging period (1.0 means no averaging)

        # Set motor speed to 0
        self.setPWM([0, 0])

    # Getters and Setters
    def setPWM(self, pwm):
        # [leftSpeed, rightSpeed]: 0 is off, caps at min and max values

        self.pwm[LEFT] = min(
            max(pwm[LEFT], self.pwmLimits[MIN]), self.pwmLimits[MAX])
        self.pwm[RIGHT] = min(
            max(pwm[RIGHT], self.pwmLimits[MIN]), self.pwmLimits[MAX])

        self._pwm_ema[LEFT] += self.pwm[LEFT] / self._ema_period
        self._pwm_ema[RIGHT] += self.pwm[RIGHT] / self._ema_period

        # Left motor
        if self.pwm[LEFT] > 0:
            GPIO.output(self.dir1Pin[LEFT], GPIO.LOW)
            GPIO.output(self.dir2Pin[LEFT], GPIO.HIGH)
            PWM.set_duty_cycle(self.pwmPin[LEFT], abs(self.pwm[LEFT]))
        elif self.pwm[LEFT] < 0:
            GPIO.output(self.dir1Pin[LEFT], GPIO.HIGH)
            GPIO.output(self.dir2Pin[LEFT], GPIO.LOW)
            PWM.set_duty_cycle(self.pwmPin[LEFT], abs(self.pwm[LEFT]))
        else:
            GPIO.output(self.dir1Pin[LEFT], GPIO.LOW)
            GPIO.output(self.dir2Pin[LEFT], GPIO.LOW)
            PWM.set_duty_cycle(self.pwmPin[LEFT], 0)

        # Right motor
        if self.pwm[RIGHT] > 0:
            GPIO.output(self.dir1Pin[RIGHT], GPIO.LOW)
            GPIO.output(self.dir2Pin[RIGHT], GPIO.HIGH)
            PWM.set_duty_cycle(self.pwmPin[RIGHT], abs(self.pwm[RIGHT]))
        elif self.pwm[RIGHT] < 0:
            GPIO.output(self.dir1Pin[RIGHT], GPIO.HIGH)
            GPIO.output(self.dir2Pin[RIGHT], GPIO.LOW)
            PWM.set_duty_cycle(self.pwmPin[RIGHT], abs(self.pwm[RIGHT]))
        else:
            GPIO.output(self.dir1Pin[RIGHT], GPIO.LOW)
            GPIO.output(self.dir2Pin[RIGHT], GPIO.LOW)
            PWM.set_duty_cycle(self.pwmPin[RIGHT], 0)

    # Methods
    def run(self):
    
    	self._adc.start()
    	
        while True:
            self.update()

            # Flash BBB LED
            if self.ledFlag is True:
                self.ledFlag = False
                GPIO.output(self.ledPin, GPIO.HIGH)
            else:
                self.ledFlag = True
                GPIO.output(self.ledPin, GPIO.LOW)
            time.sleep(self.sampleTime)

        self.cleanup()

    def cleanup(self):
        sys.stdout.write("Shutting down...")
        self.setPWM([0, 0])
        self.robotSocket.close()
        GPIO.cleanup()
        PWM.cleanup()
        self._adc.stop()
        self._adc.close()
        sys.stdout.write("Done\n")

    def update(self):
        self.readIRValues()
        self.readEncoderValues()
        self.parseCmdBuffer()

    def parseCmdBuffer(self):
        try:
            line = self.robotSocket.recv(1024)
        except socket.timeout:
            return

        self.cmdBuffer += line

        bufferPattern = r'\$[^\$\*]*?\*'  # String contained within $ and * symbols with no $ or * symbols in it
        bufferRegex = re.compile(bufferPattern)
        bufferResult = bufferRegex.search(self.cmdBuffer)

        if bufferResult:
            msg = bufferResult.group()
            print msg
            self.cmdBuffer = ''

            msgPattern = r'\$(?P<CMD>[A-Z]{3,})(?P<SET>=?)(?P<QUERY>\??)(?(2)(?P<ARGS>.*)).*\*'
            msgRegex = re.compile(msgPattern)
            msgResult = msgRegex.search(msg)

            if msgResult.group('CMD') == 'CHECK':
                self.robotSocket.sendto('Hello from QuickBot\n',(self.baseIP, self.port))

            elif msgResult.group('CMD') == 'PWM':
                if msgResult.group('QUERY'):
                    self.robotSocket.sendto(str(self.pwm) + '\n',(self.baseIP, self.port))

                elif msgResult.group('SET') and msgResult.group('ARGS'):
                    args = msgResult.group('ARGS')
                    pwmArgPattern = r'(?P<LEFT>[-]?\d+),(?P<RIGHT>[-]?\d+)'
                    pwmRegex = re.compile(pwmArgPattern)
                    pwmResult = pwmRegex.match(args)
                    if pwmResult:
                        pwm = [int(pwmRegex.match(args).group('LEFT')),
                            int(pwmRegex.match(args).group('RIGHT'))]
                        self.setPWM(pwm)

            elif msgResult.group('CMD') == 'IRVAL':
                if msgResult.group('QUERY'):
                    reply = '[' + ', '.join(map(str, self.irVal)) + ']'
                    print 'Sending: ' + reply
                    self.robotSocket.sendto(reply + '\n', (self.baseIP, self.port))

            elif msgResult.group('CMD') == 'ENVAL':
                if msgResult.group('QUERY'):
                    reply = '[' + ', '.join(map(str, self.encPos)) + ']'
                    print 'Sending: ' + reply
                    self.robotSocket.sendto(reply + '\n', (self.baseIP, self.port))

            elif msgResult.group('CMD') == 'ENVEL':
                if msgResult.group('QUERY'):
                    reply = '[' + ', '.join(map(str, self.encVel)) + ']'
                    print 'Sending: ' + reply
                    self.robotSocket.sendto(reply + '\n', (self.baseIP, self.port))

            elif msgResult.group('CMD') == 'RESET':
                self.encPos[LEFT] = 0.0
                self.encPos[RIGHT] = 0.0
                print 'Encoder values reset to [' + ', '.join(map(str, self.encVel)) + ']'

            elif msgResult.group('CMD') == 'UPDATE':
                if msgResult.group('SET') and msgResult.group('ARGS'):
                    args = msgResult.group('ARGS')
                    pwmArgPattern = r'(?P<LEFT>[-]?\d+),(?P<RIGHT>[-]?\d+)'
                    pwmRegex = re.compile(pwmArgPattern)
                    pwmResult = pwmRegex.match(args)
                    if pwmResult:
                        pwm = [int(pwmRegex.match(args).group('LEFT')),
                            int(pwmRegex.match(args).group('RIGHT'))]
                        self.setPWM(pwm)

                    reply = '[' + ', '.join(map(str, self.encPos)) + ', ' \
                        + ', '.join(map(str, self.encVel)) + ']'
                    print 'Sending: ' + reply
                    self.robotSocket.sendto(reply + '\n', (self.baseIP, self.port))

            elif msgResult.group('CMD') == 'END':
                raise StopIteration()

    def readIRValues(self):

        values = self._adc.values
        for i, x in enumerate(self.irPin):
            self.irVal[i] = values[x] * 1800 / 4096.


    def readEncoderValues(self):
        self.encCnt = self.encCnt + 1

        left_ticks = self._adc.encoder0_ticks
        left_speed = self._adc.encoder0_speed
        right_ticks = self._adc.encoder1_ticks
        right_speed = self._adc.encoder1_speed
        
        if self._pwm_ema[0] > 20:
            self.encPos[0] += left_ticks - self._last_ticks[0]
            self.encVel[0] = 121000. / left_speed
        elif self._pwm_ema[0] < -20:
            self.encPos[0] -= left_ticks - self._last_ticks[0]
            self.encVel[0] = 121000. / left_speed
        else:
            self.encVel[0] = 0

        if self._pwm_ema[1] > 20:
            self.encPos[1] += right_ticks - self._last_ticks[1]
            self.encVel[1] = 121000. / right_speed
        elif self._pwm_ema[1] < -20:
            self.encPos[1] -= right_ticks - self._last_ticks[1]
            self.encVel[1] = 121000. / right_speed
        else:
            self.encVel[1] = 0
        
        self._last_ticks = left_ticks, right_ticks


def recursiveMeanVar(x, l, mu, sigma2):
    """
    This function calculates a new mean and variance given
    the current mean "mu", current variance "sigma2", current
    update count "l", and new samples "x"
    """

    m = len(x)
    n = l + m
    muPlus = l / n * mu + m / n * np.mean(x)
    if n > 1:
        sigma2Plus = 1/(n-1) * ((l-1)*sigma2 + (m-1)*np.var(x) + l*(mu - muPlus)**2 + m*(np.mean(x) - muPlus)**2)
    else:
        sigma2Plus = 0

    return (muPlus, sigma2Plus, n)

def operatingPoint(uStar, uStarThreshold):
    """
    This function returns the steady state tick velocity given some PWM input.

    uStar: PWM input.
    uStarThreshold: Threshold on the minimum magnitude of a PWM input value

    returns: omegaStar - steady state tick velocity
    """
    # Matlab code to find beta values
    # X = [40; 80; 100]; % Air Test
    # Y = [0.85; 2.144; 3.5];
    #
    # r = 0.0325; % Wheel radius
    # c = 2*pi*r;
    # X = [  70;   70;   70;   75;   75;   75;   80;   80;   80; 85;     85;   85;   90;   90;   90]; % Ground Test
    # Z = [4.25; 3.95; 4.23; 3.67; 3.53; 3.48; 3.19; 3.08; 2.93; 2.52; 2.59; 2.56; 1.99; 2.02; 2.04]; % Time to go 1 m
    # Y = 1./(Z*c);
    # H = [X ones(size(X))];
    # beta = H \ Y
    # beta = [0.0425, -0.9504] # Air Test Results
    beta = [0.0606, -3.1475] # Ground Test Results

    if np.abs(uStar) <= uStarThreshold:
        omegaStar = 0.0
    elif uStar > 0:
        omegaStar = beta[0]*uStar + beta[1]
    else:
        omegaStar = -1.0*(beta[0]*np.abs(uStar) + beta[1])

    return omegaStar


def kalman(x, P, Phi, H, W, V, z):
    """
    This function returns an optimal expected value of the state and covariance
    error matrix given an update and system parameters.

    x:   Estimate of staet at time t-1.
    P:   Estimate of error covariance matrix at time t-1.
    Phi: Discrete time state tranistion matrix at time t-1.
    H:   Observation model matrix at time t.
    W:   Process noise covariance at time t-1.
    V:   Measurement noise covariance at time t.
    z:   Measurement at time t.

    returns: (x,P) tuple
    x: Updated estimate of state at time t.
    P: Updated estimate of error covariance matrix at time t.

    """
    x_p = Phi*x  # Prediction of setimated state vector
    P_p = Phi*P*Phi + W  # Prediction of error covariance matrix
    S = H*P_p*H + V  # Sum of error variances
    S_inv = 1/S  # Inverse of sum of error variances
    K = P_p*H*S_inv  # Kalman gain
    r = z - H*x_p  # Prediction residual
    w = -K*r  # Process error
    x = x_p - w  # Update estimated state vector
    v = z - H*x  # Measurement error
    if np.isnan(K*V):
        P = P_p
    else:
        P = (1 - K*H)*P_p*(1 - K*H) + K*V*K  # Updated error covariance matrix

    return (x, P)


def tic():
    global TICTOC_START
    TICTOC_START = time.time()


def toc(tictocName = 'toc', printFlag = True):
    global TICTOC_START
    global TICTOC_COUNT
    global TICTOC_MEAN
    global TICTOC_MAX
    global TICTOC_MIN

    tictocTime = time.time() - TICTOC_START
    TICTOC_COUNT = TICTOC_COUNT + 1
    TICTOC_MEAN = tictocTime / TICTOC_COUNT + TICTOC_MEAN * (TICTOC_COUNT-1) / TICTOC_COUNT
    TICTOC_MAX = max(TICTOC_MAX,tictocTime)
    TICTOC_MIN = min(TICTOC_MIN,tictocTime)

    if printFlag:
        print tictocName + " time: " + str(tictocTime)

def tictocPrint():
    global TICTOC_COUNT
    global TICTOC_MEAN
    global TICTOC_MAX
    global TICTOC_MIN

    print "Tic Toc Stats:"
    print "Count = " + str(TICTOC_COUNT)
    print "Mean = " + str(TICTOC_MEAN)
    print "Max = " + str(TICTOC_MAX)
    print "Min = " + str(TICTOC_MIN)


