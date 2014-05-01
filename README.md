# Quick Bot API

QuickBot is a mobile robot built as part of the Coursera "Control of the Mobile Robots" class offered by
Georgia Tech. For more information on the QuickBot platform see http://o-botics.org

This package provides high-level API to control QuickBot. Includes utilities to calibrate wheel encoders
and IR sensors.


# API overview

QB class encapsulates the API. This class can only be used at the robot side (it operates motors and reads
sensors).

QBServer is used to control robot from base station via networking (UDP). Communication protocol is
compatible with the one used in the class: http://github.com/o-botics/quickbot_bbb . This means that you should be
able to run class MatLab code. This class can be used at the robot side only.

QBClient implements the QB API by sending commands to QBServer over UDP protocol. This class is meant to
be used at the base station to control robot remotely. Since API is identical to the QB one, you can develop
and test controllers on your base computer (desktop or laptop) and then deploy the same code on QuickBot to
be run autonomously.


# Features

1. Uses hardware ADC capture, which provides high capture speed and reliable tick values with no load on CPU.

2. Unlike original robot, speed is stabilized with PID controller. This removes the need to manually adjust
torque - robot runs reliably on any surface: hardwood, carpet, asphalt.


# Configuration

All configurable parameters are in config.py file.
