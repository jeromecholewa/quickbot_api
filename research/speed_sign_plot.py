import matplotlib.pyplot as plt

data = []
with open('speed_sign.csv') as f:
	for line in f:
		data.append(tuple(float(x) for x in line.strip().split(', ')))

timer, speed_left, speed_right, ticks_left, ticks_right, torque = zip(*data)

plt.plot(timer, speed_left, color='r', label='speed (left)')
plt.plot(timer, speed_right, color='g', label='speed (right)')
plt.plot(timer, ticks_right, color='m', label='ticks (left)')
plt.plot(timer, ticks_left, color='c', label='ticks (right)')
plt.plot(timer, torque, color='b', label='torque')
plt.legend(loc=2)
plt.ylim([-60, 160])
plt.show()
