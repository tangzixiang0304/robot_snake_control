import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import serial
import math
import struct
import scipy as sp
from mpl_toolkits.mplot3d import Axes3D

ser = serial.Serial("COM4", 9600)
TIMER = time.time()


def get_angles(SX, SY):
    cs = []
    for i, j in zip(range(0, 6), range(1, 7)):
        p1 = np.array((SX[i], SY[i]))
        p2 = np.array((SX[j], SY[j]))
        r = p2 - p1
        c = r[1] / np.linalg.norm(r)
        c = c.tolist()
        cs.append(int(np.arcsin(c) * 180 / np.pi) + 180)
    # cs=sum(cs,[])

    # rs = np.arccos(rs)
    print(cs)
    print(type(cs[0]))
    send_byte = struct.pack('<B14BB', 0xbb, 180, cs[0], 180, cs[1], 180, cs[2], 180, cs[3], 180, cs[4], 180,
                            cs[5], 180, 180, 0xdd)
    print("send_byte=", send_byte)
    ser.write(send_byte)


def next(X, Y, x1, y1, i2, x2, y2, L):
    while ~((X[i2] - x1) ** 2 + (Y[i2] - y1) ** 2 - L ** 2 <= 0) or ~(
                            (X[i2 + 1] - x1) ** 2 + (Y[i2 + 1] - y1) ** 2 - L ** 2 >= 0):
        i2 += 1
    IX, IY = [np.linspace(_[i2], _[i2 + 1], 10) for _ in (X, Y)]
    I = np.argmin((IX - x2) ** 2 + (IY - y2) ** 2)
    x2, y2 = IX[I], IY[I]

    return i2, x2, y2


def main():
    global TIMER
    X = np.arange(0, 40, .005)
    Y = 0.3 * np.cos(0.5 * X)
    X = np.concatenate((np.arange(-7, 0, 0.005), X))
    Y = np.concatenate((0.3 + 0 * np.arange(-7, 0, 0.005), Y))
    L = 1
    IXY = np.arange(0, 1400, 200)
    SX, SY = X[IXY], Y[IXY]

    plt.ion()
    plt.plot(X, Y)
    plt.plot(SX, SY)
    for t in range(3000):
        I = np.argmin(np.abs(np.abs(X[IXY[0]:] - SX[0]) - 0.05))
        IXY[0] = I + IXY[0] + 1
        SX[0], SY[0] = X[IXY[0]], Y[IXY[0]]
        # print(SX[0], SY[0])

        for i in range(1, len(SX)):
            IXY[i], SX[i], SY[i] = next(X, Y, SX[i - 1], SY[i - 1], IXY[i], SX[i], SY[i], L)

        if time.time() - TIMER > 2:
            get_angles(SX, SY)
            TIMER = time.time()

        # print(theta)


        plt.cla()
        plt.plot(X, Y)
        plt.plot(SX, SY)
        plt.scatter(SX, SY)
        plt.pause(1E-6)


if __name__ == '__main__':
    main()
