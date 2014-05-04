from robot.motor import Motors
from robot.sensors import Sensors

if __name__ == '__main__':

	motors = Motors()
	sensors = Sensors()

	torque = 0

	data = []

	for _ in range(300):
		time.sleep(0.01)
		sensors.read()
		
		data.append(sensors.timer, 
			sensors.speed_left, 
			sensors.speed_right, 
			sensors.enc_ticks_left, 
			sensors.enc_ticks_right, 
			torque)

		if _ == 50:
			torque = 50
			motors.run(50)

		if _ == 150:
			torque = -50
			motors.run(-150)

		if _ == 250:
			torque = 0
			motors.run(0, 0)

	with open('speed_sign.csv', 'w') as f:
		for datum in data:
			f.write(', '.join(str(x) for x in datum) + '\n')

