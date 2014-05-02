import beaglebone_pru_adc as adc
import time
import config
from robot.motor import Motors

if __name__ == '__main__':

    adc = adc.Capture()
    adc.encoder0_pin = config.MOTOR_LEFT['encoder_pin']
    adc.encoder1_pin = config.MOTOR_RIGHT['encoder_pin']
    adc.encoder0_threshold = 4096
    adc.encoder1_threshold = 4096

    motors = Motors(config)

    adc.start()

    motors.run(60, 60)
    time.sleep(2.0)
    motors.run(0, 0)

    adc.stop()
    adc.wait()

    _, min0, max0, _, _ = adc.encoder0_values
    _, min1, max1, _, _ = adc.encoder1_values

    adc.close()

    print 'Left encoder measured range:', min0, max0, 'Recommended threshold:', int(0.9 * (max0-min0))
    print 'Right encoder measured range:', min1, max1, 'Recommended threshold:', int(0.9 * (max1-min1))