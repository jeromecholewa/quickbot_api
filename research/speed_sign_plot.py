import matplotlib.pyplot as plt

data = []
with open('speed_sign.csv') as f:
	for line in f:
		data.append(tuple(float(x) for x in line.split()))

timer, speed_left, speed_right, ticks_left, ticks_right, torque = zip(*data)

plt.plot(timer, speed_left, color='r')
plt.plot(timer, speed_right, color='g')
plt.plot(timer, ticks_right, color='m')
plt.plot(timer, ticks_left, color='c')
plt.plot(timer, torque, color='b')
plt.show()
