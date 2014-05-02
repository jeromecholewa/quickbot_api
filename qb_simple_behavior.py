"""
Simple behavior, contains three controllers:

 1. Go Straight - this controller tries to keep tick difference between right and left wheel constant, i.e. make
    bot go as straight as possible.

 2. Avoid Obstacle - this controller just stops, then backtracks a little (i.e. tries to compensate for
    bot inertia)

 3. Find New Direction - makes bot rotate on the spot, looking for a clear direction.

Bot goes straight until it hits an obstacle. It then brakes and backtracks. Then it star rotating, looking for
a direction where there is no obstacles. When found, it will run straight.
"""
import time
from qb_client import QBClient


class Signal:
    """
    Utility class: implements observer pattern. Interested parties can register their listeners and
    broadcast events.
    """

    def __init__(self):
        self._listeners = []

    def emit(self, *av, **kav):
        for l in self._listeners:
            l(*av, **kav)

    def connect(self, listener):
        self._listeners.append(listener)

    def disconnect(self, listener):
        self._listeners.remove(listener)


class GoStraightController:
    """
    Controller that tries to maintain a fixed difference between left wheel ticks and right wheel ticks.
    This makes bot go straight.

    Emits |obstacle| signal when detects an obstacle.
    """

    obstacle = Signal()

    def __init__(self, Kp=1.0, Ki=0.03, Kd=0.0, speed=50):
        self._speed = speed

    def execute(self, qb):
        if min(qb.get_ir_distances()[2:4]) < 7:  # head-on obstacle!
            qb.set_speed(0, 0)  # stop!
            self.obstacle.emit()

        else:
            qb.set_speed(self._speed, self._speed)

    def reset(self):
        pass


class AvoidCollisionController:
    """
    Measures how far bot goes after it was commanded to stop, then backtracks to compensate for this
    overshoot.

    When finished, emits |backtracked| signal.
    """

    backtracked = Signal()

    def __init__(self):
        self._timer = 0

    def reset(self):
        self._timer = 0

    def execute(self, qb):
        # backtrack to the tick position
        self._timer += 1

        if self._timer < 10:
            qb.set_speed(-50, -50)

        else:
            qb.set_speed(0, 0)
            self.backtracked.emit()


class FindNewDirectionController:
    """
    Rotates bot, looking for a direction where there is no obstacles. Whn found, emits |no_obstacle| signal.
    """

    no_obstacle = Signal()

    def __init__(self):
        self._timer = 0

    def execute(self, qb):
        self._timer += 1

        if self._timer < 10:
            if min(qb.get_ir_distances()[2:4]) > 15:
                qb.set_speed(0, 0)
                self.no_obstacle.emit()
                return

        elif self._timer > 20:
            self._timer = 0
            qb.set_speed(0, 0)
            return

        else:
            qb.set_speed(60, -60)

    def reset(self):
        self._timer = 0


class Supervisor:
    """
    Implements behavior by utilizing three controllers and managing transitions between these controllers.
    """

    def __init__(self):

        self._go_straight = GoStraightController()
        self._avoid_collision = AvoidCollisionController()
        self._find_new_direction = FindNewDirectionController()
        self.current = self._go_straight

        self._go_straight.obstacle.connect(self.on_obstacle)
        self._avoid_collision.backtracked.connect(self.on_backtracked)
        self._find_new_direction.no_obstacle.connect(self.on_no_obstacle)

    def execute(self, qb):
        return self.current.execute(qb)

    def on_obstacle(self):
        self.current = self._avoid_collision
        self.current.reset()

    def on_backtracked(self):
        self.current = self._find_new_direction
        self.current.reset()

    def on_no_obstacle(self):
        self.current = self._go_straight
        self.current.reset()


if __name__ == '__main__':

    # change the following to match your setup
    ROBOT_ADDR = ('192.168.0.9', 5005)
    BASE_ADDR = ('192.168.0.6', 5005)

    supervisor = Supervisor()

    import config

    with QBClient.connect(config.ROBOT_IP, config.BASE_IP, config.PORT) as qb:

        for _ in range(3000):
            time.sleep(0.02)

            supervisor.execute(qb)

            print qb.get_ir_distances()


        # stop motors
        qb.set_speed(0, 0)

