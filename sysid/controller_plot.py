import matplotlib.pyplot as plt

if __name__ == '__main__':

    filename = 'controller-wa-20.csv'
    #filename = 'controller-wa-40.csv'
    #filename = 'controller-wa-60.csv'
    #filename = 'controller-wa-80.csv'
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

    plt.plot(timer, reference)
    plt.plot(timer, speed, color='g')
    plt.plot(timer, control, color='r')
    plt.title('Speed')

    plt.show()
