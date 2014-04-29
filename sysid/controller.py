"""
Controller that stabilises wheel speed across all surfaces (carpet, hardwood, asphalt)
"""
import argparse
import time
import config
from sysid.encoder import Encoder
from sysid.motor import Motors
from sysid.pid import PID


class BotController(object):
    """
    This controller uses PID in a closed-loop to stabilise bot speed regardless
    of surface it is on (hard, carpet, asphalt).

    It also presents signed ticks and signed speed readings to the user, courtesy of
    Helper class (see above).

    This class expects that its on_timer() method is called at 100Hz frequency.
    """

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


class Helper(object):
    """
    Models speed dynamics to keep track of speed crossing zero - thus inferring speed and tick signs.

    Facades the real encoder values (unsigned) and presents to the user signed readings of
    ticks and speed.

    This class expects that its on_timer() method is called at 100Hz frequency (dynamical constants were
    fit using this assumption).
    """

    DT = 0.05
    ALPHA = 1.0

    def __init__(self, speed_sensor, ticks_sensor, Kp=1.0, Ki=0.1):
        self._speed = speed_sensor
        self._ticks = ticks_sensor

        self._pid = PID(Kp, Ki)
        self.torque = 0
        self.computed_torque = 0
        self.reference_speed = 0
        self._direction = 0  # direction of movement (inferred)

        self._last_ticks = None
        self._logical_ticks = 0
        self._logical_speed = 0
        self._stopping = False
        self._predicted_speed = 0

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

        old_predicted_speed = self._predicted_speed
        self._predicted_speed += self.DT * (self.torque * self._direction - self._predicted_speed
                                            + self.ALPHA * (speed - self._predicted_speed))
        if self._direction != 0 and (old_predicted_speed * self._predicted_speed < 0
                                     or 0 < self._predicted_speed < 1.0):
            # predicted speed changed sign
            self._direction = 0
            self._logical_speed = 0

        elif self._direction == 0 and self._predicted_speed >= 1.0:
            self._direction = 1 if self.torque >= 0 else -1

        delta_ticks = ticks - self._last_ticks
        self._logical_ticks += self._direction * delta_ticks
        self._logical_speed = self._direction * speed

    @property
    def ticks(self):
        return self._logical_ticks

    @property
    def speed(self):
        return self._logical_speed


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Capture encoder ticks and speed response for step rotation input')
    parser.add_argument('speed', type=int, help='speed value in the range of 0-10')
    parser.add_argument('filename', type=str, help='file name for writing CSV data')

    cmd = parser.parse_args()

    motor = BotController(config)

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

        if _ == 350:
            reference_speed = 0
            motor.run(0, 0)

        data.append( (motor.timer, reference_speed, motor.actual_speed[0], motor.actual_speed[1],
            motor._left.computed_torque, motor._right.computed_torque, motor._left.torque, motor._right.torque) )

    with open(cmd.filename, 'w') as f:
        for datum in data:
            f.write(', '.join(str(x) for x in datum) + '\n')

    print 'Data written to', cmd.filename
