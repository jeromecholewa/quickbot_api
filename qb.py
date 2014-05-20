import time
import re
import socket

from tools.fit import distance
from robot.controller import BotController


class QB(object):
    """
    Wraps BotController and presents to the user command-level API (high-level).

    Supported commands are:

    set_speed(speed_left, speed_right)

    get_ir()

    get_ticks()
    reset_ticks()

    get_speed()

    Recommended sampling frequency is 100Hz.
    """

    def __init__(self, config):
        self._bot = BotController(config)
        self._ticks_origin_left = 0
        self._ticks_origin_right = 0
        self._ir_calibration = config.IR_CALIBRATION

    def start(self):
        self._bot.start()

    def stop(self):
        self._bot.stop()

    def on_timer(self):
        self._bot.on_timer()

    def set_speed(self, speed_left, speed_right):
        self._bot.run(speed_left, speed_right)

    def get_ir_distances(self):
        return tuple( self._ir_calibration / x for x in self._bot.values )

    def get_ticks(self):
        ticks_left, ticks_right = self._bot.ticks

        return ticks_left - self._ticks_origin_left, ticks_right - self._ticks_origin_right

    def reset_ticks(self):
        self._ticks_origin_left, self._ticks_origin_right = self._bot.ticks

    def get_speed(self):
        return self._bot.actual_speed

    @classmethod
    def run(cls, config, behavior):

        qb = QB(config)
        try:

            qb.start()

            while True:
                time.sleep(0.01)
                qb.on_timer()
                behavior(qb)

        finally:
            qb.stop()


if __name__ == '__main__':
    import config

    def behavior(qb):
        print qb.get_ticks(), qb.get_ir()

    QB.run(config, behavior)
