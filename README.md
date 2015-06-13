# Quick Bot API

QuickBot is a mobile robot built as part of the Coursera "Control of the Mobile Robots" class offered by
Georgia Tech. For more information on the QuickBot platform see http://o-botics.org

This package provides high-level API to control QuickBot. Includes utilities to calibrate wheel encoders
and IR sensors. Example code implements a simple "intelligent" behavior: 
[YouTube show-off](http://youtu.be/5rOYVlgJui8).

## API overview

QB class encapsulates the API. This class can only be used at the robot side (it operates motors and reads
sensors).

QBServer - run this code on the robot side to delegate control to the base station. Communication protocol is
compatible with the one used in the class, see http://github.com/o-botics/quickbot_bbb . This means that you should be
able to run MatLab code developed in the class. This code can be used at the robot side only.

QBClient implements the QB API by sending commands to QBServer over UDP protocol. This class is meant to
be used at the base station to control robot remotely. Since API is identical to the QB one, you can develop
and test controllers on your base computer (desktop or laptop) and then deploy the same code on QuickBot to
run autonomously.


## Features

1. Uses hardware ADC capture, which provides high capture speed and reliable tick values with no load on CPU.

2. Unlike original robot, speed is stabilized with PID controller. This removes the need to manually adjust
torque - robot runs reliably on any surface: hardwood, carpet, asphalt.

3. Uses predictor/corrector to detect tick sign change (thus emulates quadrature encoder functionality in software).

## Configuration

All configurable parameters are in config.py file.

## Prerequisites

1. QuickBot

2. Install [beaglebone_pru_adc](http://github.com/pgmmpk/beaglebone_pru_adc)
    ```
    git clone http://github.com/pgmmpk/beaglebone_pru_adc
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
3. "Find clear direction" controller - robot rotates on a spot, trying to find a "clear" direction. When
   found, switches to "Go straight".

## Programming API

### QB(config)
Constructs new QB object. Takes a single parameter - configuration file.

### QB.start()
Initialises all sub-systems. Call this once before entering main loop.

### QB.on_timer()
Performs necessary periodic tasks (mostly reading sensors and maintaining encoder sign). You must call
this function at 100Hz (every 0.01 sec) in the main loop.

### QB.stop()
Cleanup of all resources.

### QB.set_speed(speed_left, speed_right)
Sets robot speed. The speed parameter is a signed float value that is desired speed of the corresponding wheel.

Speed is measured in ticks/sec. Since there are 16 encoder teeth, the speed is scaled by 16 desired number of rotations
per second. Reasonable speed range is 20-120. Range between -20 and +20 is unstable (robot physically can not move that
slow because of the mechanical limitations).

### QB.get_speed()
Returns tuple of _actual_ speed readings, not the values set with `QB.set_speed`.

### QB.get_ticks()
Returns tuple of the wheel encoder ticks. These are signed values.

### QB.reset_ticks()
Resets ticks values to zero.

### QB.get_ir()
Returns 5-tuple of raw IR readings

### QB.get_ir_distances()
Returns 5-tuple of IR readings converted to distance (in inches)

## Credits
This project started as a fork of official software http://github.com/o-botics/quickbot_bbb by Rowland O'Flaherty.

## License
MIT
