"""
Here we are calibrating IR sensors by doing some measurements, then finding
a function that converts voltage (or, more precisely, the digitized voltage readings) into
distance. Some boring math follows.

The datasheet for the sensor suggests that distance is linearly related to a biased inverse voltage. In other
terms, the following rational function should describe distance and voltage relationship:

    V = (alpha * d + beta) / (d + gamma)    (1)
or
    d = (beta - gamma * V) / (V - alpha)

where
    V - sensor output (digitized voltage)
    d - distance between object and sensor
    alpha, beta, gamma - constants

Since we have three unknown constants we need to take three measurements of voltage at (different)
distances to solve for alpha, beta, gamma.

Let V[i] i=0,1,2 be measurements corresponding to d[i] i=0,1,2. I choose

    d[0] = 3 (inches)
    d[1] = 6 (inches)
    d[2] = 12 (inches)

Re-arranging eq. 1, we get:

    alpha * d + beta - gamma * V = d * V

and substituting our measurements we get 3 linear equations:

    alpha * d[i] + beta * 1 - gamma * V[i] = d[i] * V[i],  i=0,1,2

again, we are solving for unknown alpha, beta, and gamma.

Same equation in matrix form is:

    M * (alpha, beta, gamma) = f

where matrix M is given by:

    d[0]     1      -V[0]
    d[1]     1      -V[1]              (2)
    d[2]     1      -V[2]

and vector f is:

    f = (d[0]*V[0], d[1]*V[1], d[2]*V[2])

Solution can be found if we know inverse of M, Mn1:

    Mn1 * M = I

    (alpha, beta, gamma) = Mn1 * f

Function fit(d, v) below performs all these manipulations to compute vector (alpha, beta, gamma)
"""
import numpy


def fit(d, v):
    """
    Given measurements d[i] and v[i] for i=0,1,2 computes coefficients

        alpha, beta, gamma

    such that

        v = (alpha * d + beta) / (d + gamma)

    or

        d = (beta - gamma * v) / (v - alpha)
    """

    m = numpy.matrix([
        [d[0], 1., -v[0]],
        [d[1], 1., -v[1]],
        [d[2], 1., -v[2]],
    ])

    mn1 = numpy.linalg.inv(m)

    solution = numpy.dot(mn1, numpy.array([d[0]*v[0], d[1]*v[1], d[2]*v[2]]))

    return solution[0, 0], solution[0, 1], solution[0, 2]


def distance(alpha, beta, gamma, v):
    """
    Computes distance from voltage measurement
    """
    return (beta - gamma * v) / (v - alpha)


if __name__ == '__main__':
    """
    To calibrate IR sensors do the following:

    Put bot in the center of the room (far from obstacles).

    1. Find a good "obstacle" (e.g. a book or a case). Use ruler to position this
    obstacle 3 inches from a sensor. Do the measurement of resulting voltage.

    2. Repeat for all 5 sensors

    3. Repeat again this time positioning an obstacle 6 inches away

    3. And repeat last time, positioning an obstacle 12 inches away.
    """

    ## each of total 5 sensors at 3in:
    v3  = [1005, 971, 650, 771, 836]

    ## at 6in
    v6  = [595, 579, 315, 374, 402]

    ## at 12in
    v12 = [339, 352, 87, 148, 120]

    for sensor in range(5):

        alpha, beta, gamma = fit([3, 6, 12], [v3[sensor], v6[sensor], v12[sensor]])
        for vv in [0, 10, 100, 200, 300, 400, 700, 900, 1300, 1800, 4000]:
            print '+++\t', vv, distance(alpha, beta, gamma, vv)
        print

    for sensor in range(5):
        print fit([3, 6, 12], [v3[sensor], v6[sensor], v12[sensor]])
