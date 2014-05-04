from robot.controller import BotController
import config
import time

if __name__ == '__main__':

	ctrl = BotController(config)
	ctrl.start()

	torque = 0

	data = []

	for _ in range(300):
		time.sleep(0.01)
		ctrl._sensors.read()
		ctrl._left.on_timer()
		ctrl._right.on_timer()
		
		data.append((ctrl._sensors.timer, 
			ctrl._left.speed, 
			ctrl._right.speed, 
			ctrl._left.ticks, 
			ctrl._right.ticks, 
			torque))

		if _ == 50:
			torque = 50
			ctrl._motors.run(50, 50)
			ctrl._left.run(50)
			ctrl._right.run(50)

		if _ == 150:
			torque = -50
			ctrl._motors.run(-50, -50)
			ctrl._left.run(-50)
			ctrl._right.run(-50)

		if _ == 250:
			torque = 0
			ctrl._motors.run(0, 0)
			ctrl._left.run(0)
			ctrl._right.run(0)

	with open('speed_sign2.csv', 'w') as f:
		for datum in data:
			f.write(', '.join(str(x) for x in datum) + '\n')

