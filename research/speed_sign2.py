from robot.controller import BotController
import config
import time

if __name__ == '__main__':

	SPEED = 40.0
	ctrl = BotController(config)
	ctrl.start()

	torque = 0

	data = []

	for _ in range(300):
		time.sleep(0.01)
		ctrl.on_timer()

		data.append((ctrl.timer, 
			ctrl.actual_speed[0],
			ctrl.actual_speed[1],
			ctrl.ticks[0],
			ctrl.ticks[1],
			ctrl._left.torque,
			ctrl._right.torque,
			torque))

		if _ == 50:
			torque = SPEED
			ctrl.run(SPEED, SPEED)

		if _ == 150:
			torque = -SPEED
			ctrl.run(-SPEED, -SPEED)

		if _ == 250:
			torque = 0
			ctrl.run(0, 0)

	with open('speed_sign2.csv', 'w') as f:
		for datum in data:
			f.write(', '.join(str(x) for x in datum) + '\n')

