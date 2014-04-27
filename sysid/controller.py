"""
Controller that stabilises wheel speed across all surfaces (carpet, hardwood, asphalt)
"""
import argparse
import time
import config
from sysid.encoder import Encoder
from sysid.motor import Motor
from sysid.pid import PID


class ControlledMotor:

    def __init__(self, pwm_pin, dir1_pin, dir2_pin, Kp, Ki):
        self._speed = 0  # commanded speed
        self._pid = PID(Kp, Ki)
        self._motor = Motor(pwm_pin, dir1_pin, dir2_pin)

    def feedback(self, s):
        value = self._pid.feed(self._speed - s)

        self._motor.run(value)

    def run(self, speed):
        self._speed = speed


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Capture encoder ticks and speed response for step rotation input')
    parser.add_argument('speed', type=int, help='speed value in the range of 0-10')
    parser.add_argument('filename', type=str, help='file name for writing CSV data')

    cmd = parser.parse_args()

    motor = ControlledMotor(config.MOTOR_LEFT['pwm'],
                            config.MOTOR_LEFT['dir1'],
                            config.MOTOR_LEFT['dir2'],
                            0.5, 0.05)

    encoder = Encoder(config)
    encoder.start()

    data = []
    for _ in range(200):
        time.sleep(0.01)

        encoder.read()

        actual_speed = 121000 / (encoder.enc_speed[0] + 1.0)
        data.append( (encoder.timer, cmd.speed if _ >= 50 else 0, actual_speed) )

        if _ == 50:
            motor.run(cmd.speed)

        motor.feedback(actual_speed)

    motor.run(0)

    time.sleep(1)

    with open(cmd.filename, 'w') as f:
        for datum in data:
            f.write(', '.join(str(x) for x in datum) + '\n')

    print 'Data written to', cmd.filename
