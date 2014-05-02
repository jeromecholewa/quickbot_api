# Quick Bot API

QuickBot is a mobile robot built as part of the Coursera "Control of the Mobile Robots" class offered by
Georgia Tech. For more information on the QuickBot platform see http://o-botics.org

This package provides high-level API to control QuickBot. Includes utilities to calibrate wheel encoders
and IR sensors. Example code implements a simple "intelligent" behavior.


## API overview

QB class encapsulates the API. This class can only be used at the robot side (it operates motors and reads
sensors).

QBServer is used to control robot from base station via networking (UDP). Communication protocol is
compatible with the one used in the class: http://github.com/o-botics/quickbot_bbb . This means that you should be
able to run class MatLab code. This class can be used at the robot side only.

QBClient implements the QB API by sending commands to QBServer over UDP protocol. This class is meant to
be used at the base station to control robot remotely. Since API is identical to the QB one, you can develop
and test controllers on your base computer (desktop or laptop) and then deploy the same code on QuickBot to
run autonomously.


## Features

1. Uses hardware ADC capture, which provides high capture speed and reliable tick values with no load on CPU.

2. Unlike original robot, speed is stabilized with PID controller. This removes the need to manually adjust
torque - robot runs reliably on any surface: hardwood, carpet, asphalt.


## Configuration

All configurable parameters are in config.py file.

## Prerequisites

1. QuickBot

2. Install (beaglebone_pru_adc)[http://github.com/pgmmpk/beagelbone_pru_adc]
    ```
    git clone http://github.com/pgmmpk/beagelbone_pru_adc
    cd beaglebone_pru_adc/
    python setup.py install
    ```

## Calibrating sensors

You need to calibrate wheel encoders and IR sensors. Calibration means running some simple experiments,
measuring sensor output, then entering these values into `config.py`.

### Calibrating wheel encoders

Use `tools/calibrate_wheel_encoders.py`. Just run it - it will run motors for about 2 seconds to determine
best threshold for each wheel encoder. Use these threshold values to update your `config.py`

### Calibrating IR sensors

Use `tools/calibrate_ir_sensors.py` to capture mean value of an IR sensor. You need to capture
value for 3 different distances to an obstacle: 3in, 6in, and 12in. Do this for each sensor, then
input resulting numbers into `tools/fit.py` and it will print `IR_CALIBRATION` array. Copy it and paste
into your config.py

### Other configuration

Set correct values for `ROBOT_IP`, `BASE_IP`, and `PORT` in `config.py`.

## Running simple "intelligent" behavior

On the robot side, start `qb_server.py`

On the base station, run `qb_simple_behavior.py`

Simple behavior switches between three controllers:

1. "Go straight" controller - robot travels straight until it "sees" an obstacle. Then it yields to
2. "Avoid collision" controller - robot just "jumps" back a little (this helps avoiding it getting stuck
   when too close to a wall). Then it switches to
3. "Find clear direction" controller - robot rotates on a spot, trying to find an "clear" direction. When
   found, switches to "Go straight".

## License
MIT