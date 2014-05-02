import beaglebone_pru_adc as adc
import time
import collections
import config
from robot.motor import Motors

if __name__ == '__main__':

    adc = adc.Capture()

    ir_pins = config.IR_PINS

    adc.start()

    stat = collections.defaultdict(list)

    for _ in range(1000):
        time.sleep(0.005)
        values = adc.values
        for i, pin in enumerate(ir_pins):
            stat[i].append(values[pin])

    adc.stop()
    adc.wait()

    _, min0, max0, _, _ = adc.encoder0_values
    _, min1, max1, _, _ = adc.encoder1_values

    adc.close()

    for i in range(len(ir_pins)):
        mean = sum(stat[i]) / len(stat[i])
        min_ = min(stat[i])
        max_ = max(stat[i])

        print '#%d: RANGE: %4.2lf -- %4.2lf, MEAN: %4.2lf' % (i, min_, max_, mean)