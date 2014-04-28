"""
Controller that stabilises wheel speed across all surfaces (carpet, hardwood, asphalt)
"""
import argparse
import time
import config
from sysid.encoder import Encoder
from sysid.motor import Motors
from sysid.pid import PID


class Helper(object):

    def __init__(self, speed_sensor, ticks_sensor, Kp=1.0, Ki=0.1):
        self._speed = speed_sensor
        self._ticks = ticks_sensor

        self._pid = PID(Kp, Ki)
        self.torque = 0
        self.reference_speed = 0
        self._direction = 0  # direction of movement. used to infer sign of speed and ticks

        self._last_ticks = None
        self._logical_ticks = 0
        self._logical_speed = 0
        self._stopping = False

    def run(self, speed):
        self.reference_speed = speed

    def on_timer(self):
        self.torque = self._pid.feed(self.reference_speed - self._logical_speed)
        self.computed_torque = self.torque

        ticks = self._ticks()
        speed = self._speed()

        if self._last_ticks is None:
            self._last_ticks = ticks
            return

        if self._last_ticks == ticks:
            return

        if self._stopping:
            self.torque = 0
            if speed < 5.0:
                self._stopping = False  # stopped
                self._direction = 0

        else:

            if self._direction == 0:
                if abs(self.torque) > 10.0:
                    # will be moving soon!
                    self._direction = 1 if self.torque > 0 else -1

            elif self._direction == 1:
                if self.reference_speed < 10.0:
                    # reversing (may be active braking)
                    # prepare for the change in sign
                    self._stopping = True

            else:
                assert self._direction == -1
                if self.reference_speed > -10.0:
                    # reversing or active braking
                    self._stopping = True

        delta_ticks = ticks - self._last_ticks
        self._logical_ticks += self._direction * delta_ticks
        self._logical_speed = self._direction * speed

    @property
    def ticks(self):
        return self._logical_ticks

    @property
    def speed(self):
        return self._logical_speed


class SmartMotors(object):

    def __init__(self, config, Kp=1.0, Ki=0.0):
        self._motors = Motors(config)
        self._encoder = Encoder(config)
        self._encoder.start()

        def left_speed():
            # ADC capture is running at 121K adc timer units per second. And captured speed is an inverse
            # (i.e. number of timer units since the last tick was registered)
            return 121000 / (self._encoder.enc_speed[0] + 1.0)

        def left_ticks():
            return self._encoder.enc_ticks[0]

        def right_speed():
            return 121000 / (self._encoder.enc_speed[1] + 1.0)

        def right_ticks():
            return self._encoder.enc_ticks[1]

        self._left = Helper(speed_sensor=left_speed, ticks_sensor=left_ticks)
        self._right = Helper(speed_sensor=right_speed, ticks_sensor=right_ticks)

    def on_timer(self):
        self._encoder.read()

        self._left.on_timer()
        self._right.on_timer()
        self._motors.run(self._left.torque, self._right.torque)

    def run(self, speed_left, speed_right):
        self._left.run(speed_left)
        self._right.run(speed_right)

    @property
    def ticks(self):
        return self._left.ticks, self._right.ticks

    @property
    def actual_speed(self):
        return self._left.speed, self._right.speed

    @property
    def timer(self):
        return self._encoder.timer

    @property
    def values(self):
        return self._encoder.values


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Capture encoder ticks and speed response for step rotation input')
    parser.add_argument('speed', type=int, help='speed value in the range of 0-10')
    parser.add_argument('filename', type=str, help='file name for writing CSV data')

    cmd = parser.parse_args()

    motor = SmartMotors(config)

    data = []
    reference_speed = 0
    for _ in range(400):
        time.sleep(0.01)

        motor.on_timer()

        if _ == 50:
            reference_speed = cmd.speed
            motor.run(cmd.speed, cmd.speed)

        if _ == 200:
            reference_speed = -cmd.speed
            motor.run(-cmd.speed, -cmd.speed)

        data.append( (motor.timer, reference_speed, motor.actual_speed[0], motor.actual_speed[1],
            motor._left.computed_torque, motor._right.computed_torque, motor._left.torque, motor._right.torque) )

    with open(cmd.filename, 'w') as f:
        for datum in data:
            f.write(', '.join(str(x) for x in datum) + '\n')

    print 'Data written to', cmd.filename
