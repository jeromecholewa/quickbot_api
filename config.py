#
# Pin assignments for QuickBot
#
BASE_IP = '192.168.0.6'
ROBOT_IP = '192.168.0.9'
PORT = 5005

MOTOR_LEFT = {
    'dir1': 'P8_14',
    'dir2': 'P8_16',
    'pwm' : 'P9_16',

    'encoder_pin'      : 0,  # AIN0
    'encoder_threshold': 3000,
    'encoder_delay'    : 50
}

MOTOR_RIGHT = {
    'dir1': 'P8_12',
    'dir2': 'P8_10',
    'pwm' : 'P9_14',

    'encoder_pin'      : 2,  # AIN2
    'encoder_threshold': 2500,
    'encoder_delay'    : 50
}

IR_PINS = (3, 1, 5, 6, 4)  # AIN3, AIN1, AIN5, AIN6, AIN4

EMA_POW = 11  # 2**EMA_POW is the averaging time (in ADC timer ticks)
              # of IR readings. ADC timer runs at about 120000 ticks per second

# IR sensor calibration constants (see fit.py)
IR_CALIBRATION = [
    (36.702127659574444, 3995.4255319148942, 1.085106382978724),
    (99.732495511669754, 3262.2980251346507, 0.66786355475763237),
    (-203.41628959275999, 3627.8959276018086, 1.642533936651585),
    (-99.883802816901323, 3060.5915492957743, 0.58098591549295753),
    (-224.55972696245738, 4294.4436860068263, 1.3310580204778155),
]

