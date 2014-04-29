import matplotlib.pyplot as plt

if __name__ == '__main__':

    #filename = 'controller-wa-20.csv'
    filename = 'controller-wa-40.csv'
    filename = 'controller-wa-60.csv'
    filename = 'controller-wa-80.csv'
    #filename = 'controller-wa-100.csv'
    #filename = 'controller-wa-120.csv'
    #filename = 'controller-wa-150.csv'

    data = []
    with open(filename, 'r') as f:
        for line in f:
            data.append(tuple(float(x.strip()) for x in line.split(',')))

    timer = [d[0] for d in data]
    reference = [d[1] for d in data]
    speed = [d[2] for d in data]
    control = [d[3] for d in data]

    DT = 0.05
    ALPHA = 2.0

    pspeed = []
    prev_s = None
    predicted_speed = 0
    direction = 1
    for r, s in zip(reference, speed):
        old_speed = predicted_speed
        predicted_speed += DT * (r * direction - predicted_speed + ALPHA * (abs(s) - predicted_speed))
        if direction != 0 and (old_speed * predicted_speed < 0 or 0 < predicted_speed < 1.0):
            direction = 0
            predicted_speed = 0
        elif direction == 0 and predicted_speed >= 1.0:
            direction = 1 if r >= 0 else -1

        pspeed.append(predicted_speed * direction)

    plt.plot(timer, reference)
    plt.plot(timer, speed, color='g')
    plt.plot(timer, control, color='r')
    plt.plot(timer, pspeed, color='m')
    plt.title('Speed')

    plt.show()
