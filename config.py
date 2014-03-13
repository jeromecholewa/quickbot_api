#
# Pin assignments for QuickBot
#
BASE_IP = '192.168.0.8'
ROBOT_IP = '192.168.0.9'
PORT = 5005

MOTOR_LEFT = {
    'dir1': 'P8_14',
    'dir2': 'P8_16',
    'pwm' : 'P9_16',

    'threshold': 2500
}

MOTOR_RIGHT = {
    'dir1': 'P8_12',
    'dir2': 'P8_10',
    'pwm' : 'P9_14',

    'threshold': 2500
}

# Bot speed is roughly estimated from PWM signal by applying EMA-averaging over
# this period. For example, if PWM goes from zero to 100, speed does not immediately
# catch up, because of the inertia. EMA models this inertia. This estimate is used
# for suppressing encoder readings when bot is not moving (or some noise may result in
# bogus readings). Time value of one period is 0.005 sec. Therefore, set period to 100
# to introduce 0.5sec inertia lag.
PWM_EMA_PERIOD = 1.0