import beaglebone_pru_adc as adc
import time
import collections
import sys
import config
from robot.motor import Motors

if __name__ == '__main__':

    print 'Capturing IR values, wait 5 seconds\n',

    adc = adc.Capture()
    adc.ema_pow = 10
    scale = 2 ** 10

    ir_pins = config.IR_PINS

    adc.start()

    stat = collections.defaultdict(list)

    time.sleep(0.1)

    for _ in range(1000):
        if _ % 200 == 199:
            sys.stdout.write('.')
            sys.stdout.flush()
        time.sleep(0.005)
        values = adc.values
        for i, pin in enumerate(ir_pins):
            stat[i].append(values[pin] / scale)
    print

    adc.stop()
    adc.wait()

    _, min0, max0, _, _ = adc.encoder0_values
    _, min1, max1, _, _ = adc.encoder1_values

    adc.close()

    for i in range(len(ir_pins)):
        mean = sum(stat[i]) / len(stat[i])
	median = sorted(stat[i])[len(stat[i])/2]
        min_ = min(stat[i])
        max_ = max(stat[i])

	print '#%d: RANGE: %4.2lf--%4.2lf, MEAN: %4.2lf, MEDIAN: %4.2lf' % (i, min_, max_, mean, median)

	with open('x%s.csv' % i, 'wb') as f:
            f.write('\n'.join(str(x) for x in stat[i]))
