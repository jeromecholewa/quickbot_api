#
# Pin assignments for QuickBot
#
BASE_IP = '192.168.0.8'
ROBOT_IP = '192.168.0.7'
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
