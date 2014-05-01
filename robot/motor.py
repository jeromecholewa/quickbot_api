import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM


class Motor:
    """
    Helper class that controls one motor speed
    """

    def __init__(self, pwm_pin, dir1_pin, dir2_pin, max_speed=100):
        """

        """
        self.speed = 0
        self.max_speed = max_speed

        self._pwm_pin = pwm_pin
        self._dir1_pin = dir1_pin
        self._dir2_pin = dir2_pin

        GPIO.setup(self._dir1_pin, GPIO.OUT)
        GPIO.setup(self._dir2_pin, GPIO.OUT)
        PWM.start(self._pwm_pin, 0)
        PWM.set_duty_cycle(self._pwm_pin, 0)

    def close(self):
        PWM.set_duty_cycle(self._pwm_pin, 0)

    @classmethod
    def cleanup(cls):
        PWM.cleanup()
        GPIO.cleanup()

    def run(self, speed):
        """
        Makes motor to run (or stop).

        Parameters:

            |speed| is a float value in the range [-100.0, 100.0].
            Zero means "stop motor"
            100.0 means "run forward at full speed"
            -100.0 means "run backward at full speed"
        """
        self.speed = min(max(speed, -self.max_speed), self.max_speed)

        if self.speed > 0:
            GPIO.output(self._dir1_pin, GPIO.LOW)
            GPIO.output(self._dir2_pin, GPIO.HIGH)
            PWM.set_duty_cycle(self._pwm_pin, abs(self.speed))
        elif self.speed < 0:
            GPIO.output(self._dir1_pin, GPIO.HIGH)
            GPIO.output(self._dir2_pin, GPIO.LOW)
            PWM.set_duty_cycle(self._pwm_pin, abs(self.speed))
        else:
            GPIO.output(self._dir1_pin, GPIO.LOW)
            GPIO.output(self._dir2_pin, GPIO.LOW)
            PWM.set_duty_cycle(self._pwm_pin, 0)


class Motors:

    def __init__(self, config):

        self._motor_left = Motor(
            config.MOTOR_LEFT['pwm'],
            config.MOTOR_LEFT['dir1'],
            config.MOTOR_LEFT['dir2']
        )

        self._motor_right = Motor(
            config.MOTOR_RIGHT['pwm'],
            config.MOTOR_RIGHT['dir1'],
            config.MOTOR_RIGHT['dir2']
        )

    def run(self, speed_left, speed_right):

        self._motor_left.run(speed_left)
        self._motor_right.run(speed_right)

    def close(self):
        self._motor_left.close()
        self._motor_right.close()
        Motor.cleanup()