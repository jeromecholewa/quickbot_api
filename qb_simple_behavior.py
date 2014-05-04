"""
Simple behavior, contains three controllers:

 1. Go Straight - this controller tries to keep tick difference between right
    and left wheel constant, i.e. make bot go as straight as possible.

 2. Avoid Obstacle - this controller just stops, then backtracks a little
    (i.e. tries to compensate for bot inertia)

 3. Find New Direction - makes bot rotate on the spot, looking for a
    clear direction.

Bot goes straight until it hits an obstacle. It then brakes and backtracks.
Then it start rotating, looking for a direction where there is no obstacles.
When found, it will run straight.
"""
import time
from qb_client import QBClient


class Signal:
    """
    Utility class: implements observer pattern. Interested parties can register
    their listeners and broadcast events.
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
    Controller that just goes straigh until it "sees" an head-on obstacle.
    Emits |obstacle| signal when detects an obstacle.
    """

    obstacle = Signal()

    def __init__(self, speed=50, distance_threshold=7):
        self._speed = speed
        self._distance_threshold = distance_threshold

    def execute(self, qb):
        if min(qb.get_ir_distances()[2:4]) < self._distance_threshold:
            # head-on obstacle!
            qb.set_speed(0, 0)  # stop!
            self.obstacle.emit()

        else:
            qb.set_speed(self._speed, self._speed)

    def reset(self):
        pass


class AvoidCollisionController:
    """
    Reverses direction trying to establish some distance from the obstacle.

    When finished, emits |backtracked| signal.
    """

    backtracked = Signal()

    def __init__(self, speed=50, distance_threshold=10):
        self._speed = speed
        self._distance_threshold = distance_threshold
        self._timer = 0

    def reset(self):
        self._timer = 0

    def execute(self, qb):
        # backtrack to the tick position
        self._timer += 1

        if self._timer < self._distance_threshold:
            qb.set_speed(-self._speed, -self._speed)

        else:
            qb.set_speed(0, 0)
            self.backtracked.emit()


class FindNewDirectionController:
    """
    Rotates bot, looking for a direction where there is no obstacles. When
    found, emits |no_obstacle| signal.
    """

    no_obstacle = Signal()

    def __init__(self,
                 speed=50,
                 pause_duration=10,
                 move_duration=10,
                 distance_threshold=15):
        self._speed = speed
        self._pause_duration = pause_duration
        self._move_duration = move_duration
        self._distance_threshold = distance_threshold
        self._timer = 0

    def execute(self, qb):
        self._timer += 1

        if self._timer < self._pause_duration:
            if min(qb.get_ir_distances()[2:4]) > self._distance_threshold:
                qb.set_speed(0, 0)
                self.no_obstacle.emit()
                return

        elif self._timer > self._pause_duration + self._move_duration:
            self._timer = 0
            qb.set_speed(0, 0)
            return

        else:
            qb.set_speed(self._speed, -self._speed)

    def reset(self):
        self._timer = 0


class Supervisor:
    """
    Implements behavior by utilizing three controllers and managing
    transitions between these controllers.
    """

    def __init__(self, config):

        self._go_straight = GoStraightController(
            speed=config.GO_STRAIGHT['speed'],
            distance_threshold=config.GO_STRAIGHT['distance_threshold']
        )

        self._avoid_collision = AvoidCollisionController(
            speed=config.AVOID_COLLISION['speed'],
            distance_threshold=config.AVOID_COLLISION['distance_threshold']
        )

        self._find_new_direction = FindNewDirectionController(
            speed=config.FIND_NEW_DIRECTION['speed'],
            pause_duration=config.FIND_NEW_DIRECTION['pause_duration'],
            move_duration=config.FIND_NEW_DIRECTION['move_duration'],
            distance_threshold=config.FIND_NEW_DIRECTION['distance_threshold']
        )

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

    import config

    supervisor = Supervisor(config)

    with QBClient.connect(config.ROBOT_IP, config.BASE_IP, config.PORT) as qb:

        for _ in range(3000):
            time.sleep(0.02)

            supervisor.execute(qb)

            print qb.get_ir_distances()

        # stop motors
        qb.set_speed(0, 0)
