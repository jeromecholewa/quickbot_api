"""
QuickBot sensors.

Presently all sensors are based on internal ADC
"""

import beaglebone_pru_adc as adc


class Sensors:
    """
    Represents raw QuickBot sensors. "Raw" means that ticks and speed are unsigned, as read
    from the hardware.
    """

    TIMERTICKS_PER_SEC = 121000.0  # that many timer ticks per second

    def __init__(self, config):

        # Initialize ADC
        self._adc = adc.Capture()
        self._adc.encoder0_pin = config.MOTOR_LEFT['encoder_pin']
        self._adc.encoder1_pin = config.MOTOR_RIGHT['encoder_pin']
        self._adc.encoder0_threshold = config.MOTOR_LEFT['encoder_threshold']
        self._adc.encoder1_threshold = config.MOTOR_RIGHT['encoder_threshold']
        self._adc.encoder0_delay = config.MOTOR_LEFT['encoder_delay']
        self._adc.encoder1_delay = config.MOTOR_RIGHT['encoder_delay']
        self._adc.ema_pow = config.EMA_POW

        self._ir_pins = config.IR_PINS
        self._scale = 2**config.EMA_POW

        self.timer = 0
        self.speed_left = 0
        self.speed_right = 0
        self.enc_ticks_left = 0
        self.enc_ticks_right = 0
        self.values = tuple([0] * len(self._ir_pins))

    def start(self):
        self._adc.start()

    def stop(self):
        self._adc.stop()

    def read(self):
        self.timer = self._adc.timer
        self.enc_ticks_left = self._adc.encoder0_ticks
        self.enc_ticks_right = self._adc.encoder1_ticks

        # ADC capture is running at 121K adc timer units per second. And captured speed is an inverse
        # (i.e. number of timer units since the last tick was registered)
        self.speed_left = self.TIMERTICKS_PER_SEC / (self._adc.encoder0_speed + 1.0)
        self.speed_right = self.TIMERTICKS_PER_SEC / (self._adc.encoder1_speed + 1.0)

        values = self._adc.values
        self.values = tuple(float(values[x])/self._scale for x in self._ir_pins)
