import matplotlib.pyplot as plt

data = []
with open('speed_sign2.csv') as f:
#with open('speed_sign2_carpet.csv') as f:
	for line in f:
		data.append(tuple(float(x) for x in line.strip().split(', ')))

timer, speed_left, speed_right, ticks_left, ticks_right, torque = zip(*data)
timer = [x / 120000 for x in timer]

plt.plot(timer, speed_left, color='r', label='speed (left)')
plt.plot(timer, speed_right, color='g', label='speed (right)')
plt.plot(timer, ticks_right, color='m', label='ticks (left)')
plt.plot(timer, ticks_left, color='c', label='ticks (right)')
plt.plot(timer, torque, color='b', label='torque')
plt.legend(loc=3)
plt.ylim([-80, 100])
plt.show()
