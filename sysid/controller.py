"""
Controller that stabilises wheel speed across all surfaces (carpet, hardwood, asphalt)
"""
import argparse
import time
import config
from sysid.encoder import Encoder
from sysid.motor import Motor, Motors
from sysid.pid import PID


class SmartMotors(object):

    def __init__(self, config, Kp=1.0, Ki=0.095):
        self._motors = Motors(config)
        self._encoder = Encoder(config)
        self._encoder.start()
        self.reference_speed_left = 0
        self.reference_speed_right = 0
        self._pid_left = PID(Kp, Ki)
        self._pid_right = PID(Kp, Ki)

    def on_timer(self):
        self._encoder.read()

        actual_speed_left, actual_speed_right = self.actual_speed

        torque_left = self._pid_left.feed(self.reference_speed_left - actual_speed_left)
        torque_right = self._pid_right.feed(self.reference_speed_right - actual_speed_right)

        self._motors.run(torque_left, torque_right)

    def run(self, speed_left, speed_right):
        self.reference_speed_left, self.reference_speed_right = speed_left, speed_right

    @property
    def ticks(self):
        return self._encoder.enc_ticks

    @property
    def actual_speed(self):
        # ADC capture is running at 121K adc timer units per second. And captured speed is an inverse
        # (i.e. number of timer units since the last tick was registered)
        return 121000 / (self._encoder.enc_speed[0] + 1.0), 121000 / (self._encoder.enc_speed[1] + 1.0)

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
    for _ in range(200):
        time.sleep(0.01)

        motor.on_timer()

        if _ == 50:
            motor.run(cmd.speed, cmd.speed)

        data.append( (motor.timer, cmd.speed if _ >= 50 else 0, motor.actual_speed) )

    motor.run(0, 0)

    time.sleep(1)

    with open(cmd.filename, 'w') as f:
        for datum in data:
            f.write(', '.join(str(x) for x in datum) + '\n')

    print 'Data written to', cmd.filename
