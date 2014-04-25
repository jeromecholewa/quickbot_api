"""
System identification for QuickBot v1

Need precise timing, hence run this on QB side
"""
import argparse
import time
import config
from sysid.encoder import Encoder
from sysid.motor import Motors

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Capture encoder ticks and speed response for step torque input')
    parser.add_argument('torque', type=int, help='torque value in the range of 0-100', default=80)
    parser.add_argument('filename', type=str, help='file name for writing CSV data', default='sysid.csv')

    cmd = parser.parse_args()

    encoder = Encoder(config)
    motors = Motors(config)

    encoder.start()

    data = []
    for _ in range(200):
        time.sleep(0.01)

        encoder.read()

        data.append((encoder.timer,
                     encoder.enc_ticks[0],
                     encoder.enc_ticks[1],
                     encoder.enc_speed[0],
                     encoder.enc_speed[1]))

        if _ == 50:
            motors.run(cmd.torque, cmd.torque)

    motors.run(0, 0)

    with open(cmd.filename, 'w') as f:
        for datum in data:
            f.write(', '.join(str(x) for x in datum) + '\n')

    print 'Data written to', cmd.filename
