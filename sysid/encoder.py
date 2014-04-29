import beaglebone_pru_adc as adc


class Encoder:

    def __init__(self, config):

        # Initialize ADC
        self._adc = adc.Capture()
        self._adc.encoder0_pin = config.MOTOR_LEFT['encoder_pin']
        self._adc.encoder1_pin = config.MOTOR_RIGHT['encoder_pin']
        self._adc.encoder0_threshold = config.MOTOR_LEFT['encoder_threshold']
        self._adc.encoder1_threshold = config.MOTOR_RIGHT['encoder_threshold']
        self._adc.encoder0_delay = config.MOTOR_LEFT['encoder_delay']
        self._adc.encoder1_delay = config.MOTOR_RIGHT['encoder_delay']

        self.timer = 0
        self.enc_speed = [0, 0]
        self.enc_ticks = [0, 0]
        self.values = (0, 0, 0, 0, 0)

    def start(self):
        self._adc.start()

    def stop(self):
        self._adc.stop()

    def read(self):
        self.timer = self._adc.timer
        self.enc_ticks[0] = self._adc.encoder0_ticks
        self.enc_ticks[1] = self._adc.encoder1_ticks
        self.enc_speed[0] = self._adc.encoder0_speed
        self.enc_speed[1] = self._adc.encoder1_speed
        self.values = self._adc.values
