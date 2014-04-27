import matplotlib.pyplot as plt

if __name__ == '__main__':

    filename = 'run-carpet-70.csv'  # A=0.00026   t0=30000
    filename = 'run-carpet-80.csv'  # A=0.00034   t0=32000
    filename = 'run-carpet-90.csv'  # A=0x00046   t0=20000
    filename = 'run-carpet-100.csv' # A=0x00066   t0=20000

    filename = 'run-wa-70.csv'      # A=0.00050   t0=17000
    #filename = 'run-wa-80.csv'      # A=0.00059   t0=14500
    #filename = 'run-wa-90.csv'      # A=0.00068   t0=11000
    #filename = 'run-wa-100.csv'     # A=0.00085   t0=10000

    #filename = 'sysid-hard-70.csv'    # A=0.00035   t0=27000
    #filename = 'sysid-hard-80.csv'    # A=0.00042   t0=34000
    #filename = 'sysid-hard-90.csv'    # A=0.00056   t0=23000
    #filename = 'sysid-hard-100.csv'   # A=0.00075   t0=31000

    #filename = 'rotate-wa-70.csv'
    #filename = 'rotate-wa-80.csv'
    #filename = 'rotate-wa-90.csv'
    #filename = 'rotate-wa-100.csv'

    #filename = 'rotate-carpet-70.csv'
    #filename = 'rotate-carpet-80.csv'
    #filename = 'rotate-carpet-90.csv'
    #filename = 'rotate-carpet-100.csv'

    data = []
    with open(filename, 'r') as f:
        for line in f:
            data.append(tuple(int(x.strip()) for x in line.split(',')))

    timer = [d[0] for d in data]
    ticks_left = [d[1] for d in data]
    ticks_right = [d[2] for d in data]
    speed_left = [d[3] for d in data]
    speed_right = [d[4] for d in data]

    # speed sometimes returns small numbers? like 1 or 3, when at rest => check software bug in driver
    speed_left = [x if x > 100 else 200000 for x in speed_left]
    speed_right = [x if x > 100 else 200000 for x in speed_right]

    plt.subplot(2, 1, 1)
    plt.plot(timer, ticks_left)
    plt.plot(timer, ticks_right, color='r')
    plt.plot([timer[50]], [10], 'ob')
    plt.title('Ticks')

    plt.subplot(2, 1, 2)
    plt.plot(timer, [1.0 / (x + 0.0001) for x in speed_left])
    plt.plot(timer, [1.0 / (x + 0.0001) for x in speed_right], color='r')
    plt.plot([timer[50]], [0.0001], 'ob')
    plt.title('Speed')

    plt.show()
