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
def get_angles(SX, SY, SZ):
    rs = []
    for i, j in zip(range(0, 5), range(1, 6)):
        p1 = np.array((SX[i], SY[i], SZ[i]))
        p2 = np.array((SX[j], SY[j], SZ[j]))
        r = p2 - p1
        r /= np.linalg.norm(r)
        rs.append(r)
    print(rs)
    print(type(rs[0]))
    send_byte = struct.pack('<B14BB', 0x0a, rs[0], rs[1], rs[2], rs[3], rs[4], rs[5], rs[6], rs[7], rs[8], rs[9], 0x00,
                             0x00, 0x00, 0x00, 0x0d)
    ser.write(send_byte)


def next(X, Y, Z, x1, y1, z1, i2, x2, y2, z2, L):
    while ~((X[i2] - x1) ** 2 + (Y[i2] - y1) ** 2 + (Z[i2] - z1) ** 2 - L ** 2 <= 0) or ~(
                                (X[i2 + 1] - x1) ** 2 + (Y[i2 + 1] - y1) ** 2 + (Z[i2 + 1] - z1) ** 2 - L ** 2 >= 0):
        print((X[i2] - x1) ** 2 + (Y[i2] - y1) ** 2 + (Z[i2] - z1) ** 2 - L ** 2,
              (X[i2 + 1] - x1) ** 2 + (Y[i2 + 1] - y1) ** 2 + (Z[i2 + 1] - z1) ** 2 - L ** 2)
        i2 += 1
    IX, IY, IZ = [np.linspace(_[i2], _[i2 + 1], 10) for _ in (X, Y, Z)]
    I = np.argmin((IX - x2) ** 2 + (IY - y2) ** 2 + (IZ - z2) ** 2)
    x2, y2, z2 = IX[I], IY[I], IZ[I]

    return i2, x2, y2, z2


def main():
    global TIMER
    Z = np.arange(0, 40, .005)
    X = 5. * np.sin(0.5 * Z)
    Y = 6. * np.cos(0.5 * Z)
    X=np.concatenate((np.arange(-6,0,0.005),X))
    Y=np.concatenate((6+0*np.arange(-6,0,0.005),Y))
    Z=np.concatenate((0*np.arange(-6,0,0.005),Z))
    # I = X < 7
    # Z[I] = -6
    # Y[I] = X[I][::-1]
    # X[I] = 7
    L = 1
    IXY = np.arange(0, 1200, 200)
    SX, SY, SZ = X[IXY], Y[IXY], Z[IXY]

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.axis('equal')
    ax.plot(X, Y, Z)
    ax.plot(SX, SY, SZ)
    for t in range(3000):
        I = np.argmin(np.abs(np.abs(X[IXY[0]:] - SX[0]) - 0.05))  # 第一个点往前走0.05
        IXY[0] = I + IXY[0] + 1
        SX[0], SY[0], SZ[0] = X[IXY[0]], Y[IXY[0]], Z[IXY[0]]
        # print(SX[0], SY[0])

        for i in range(1, len(SX)):
            IXY[i], SX[i], SY[i], SZ[i] = next(X, Y, Z, SX[i - 1], SY[i - 1], SZ[i - 1], IXY[i], SX[i], SY[i], SZ[i], L)

        # theta = np.arctan2(SY[1:] - SY[:-1], SX[1:] - SX[:-1])
        # theta[1:] = theta[1:] - theta[: -1]
        if time.time() - TIMER > 1:
            get_angles(SX, SY, SZ)
            TIMER = time.time()

        # print(theta)

        ax.clear()
        ax.plot(X, Y, Z)
        ax.plot(SX, SY, SZ)
        # plt.plot(X, Y,)
        # plt.plot(SX, SY)
        ax.scatter(SX, SY,SZ)
        # plt.scatter(SX, SY)
        plt.pause(1E-6)


if __name__ == '__main__':
    main()
