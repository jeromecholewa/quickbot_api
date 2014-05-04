from robot.motor import Motors
from robot.sensors import Sensors
import config
import time

if __name__ == '__main__':

	SPEED = 40

	motors = Motors(config)
	sensors = Sensors(config)
	sensors.start()

	torque = 0

	data = []

	for _ in range(300):
		time.sleep(0.01)
		sensors.read()
		
		data.append((sensors.timer, 
			sensors.speed_left, 
			sensors.speed_right, 
			sensors.enc_ticks_left, 
			sensors.enc_ticks_right, 
			torque))

		if _ == 50:
			torque = SPEED
			motors.run(SPEED, SPEED)

		if _ == 150:
			torque = -SPEED
			motors.run(-SPEED, -SPEED)

		if _ == 250:
			torque = 0
			motors.run(0, 0)

	with open('speed_sign.csv', 'w') as f:
		for datum in data:
			f.write(', '.join(str(x) for x in datum) + '\n')

