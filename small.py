import time
import struct
import serial

ser = serial.Serial("COM4", 9600)
TIME = 1.3
send_bytes = (180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180)
# changes=[(1,2,-10),(2,2,-10),(3,2,-10),(5,2,-10),(6,1,-10),(5,1,-10),(4,1,-10),(3,1,-10)]
change_2d = [(1, 2, -10), (2, 2, -10), (3, 2, -10), (5, 2, -10), (6, 1, -10), (5, 1, -10), (4, 1, -10), (3, 1, -10)]
change_1d = [(1, 2, -10), (2, 2, -10), (3, 2, -10), (5, 2, -10)]
# come_go=[(6,1,-10),(6,1,0),(5,1,-10),(5,1,0),(4,1,-10),(4,1,0),(3,1,-10),(3,1,0),(2,1,-10),(2,1,0),(1,1,-10),(1,1,0)]
come_go = [(6, 2, -10), (6, 2, 0), (5, 2, -10), (5, 2, 0), (4, 2, -10), (4, 2, 0), (3, 2, -10), (3, 2, 0), (2, 2, -10),
           (2, 2, 0), (1, 2, -10), (1, 2, 0)]
# changes_sophere = [(1, 0, -10), (1, , -5), (1, 1, 10), (1, 2, 10)]
incline = [(6, -20, -10), (6, 0, 0), (5, -20, -10), (5, 0, 0), (4, -20, -10), (4, 0, 0), (3, -20, -10), (3, 0, 0),
           (2, -20, -10), (2, 0, 0), (1, -20, -10), (1, 0, 0)]


def get_sophere(n,x):
    one_list = [1, ]
    for i in range(n,x):





def change_to_zero(the_list):
    print("reverse_start")
    the_list.reverse()
    for i in the_list:
        r_list = list(i)
        r_list[2] = 0
        r_tuple = tuple(r_list)
        change(*r_tuple)


def change(a, b, c):
    global send_bytes
    replace = list(send_bytes)
    replace[2 * (a - 1) + b - 1] = 180 + c
    send_bytes = tuple(replace)
    send_byte = struct.pack('16B', 0xbb, *send_bytes, 0x00, 0x00, 0xdd)
    ser.write(send_byte)
    # print (send_bytes)
    print(send_byte)
    time.sleep(TIME)


def change_loc(a, b, c):
    global send_bytes
    replace = list(send_bytes)
    replace[2 * (a - 1)] = 180 + b
    replace[2 * (a - 1) + 1] = 180 + c
    send_bytes = tuple(replace)
    send_byte = struct.pack('16B', 0xbb, *send_bytes, 0x00, 0x00, 0xdd)
    ser.write(send_byte)
    # print (send_bytes)
    print(send_byte)
    time.sleep(TIME)


def run(the_list, a):
    if a == True:
        for i in the_list:
            change(*i)
    else:
        for i in the_list:
            change_loc(*i)


run(change_2d, True)
time.sleep(10)
change_to_zero(change_2d)
# 0A B4 AA B4 AA B4 AA AA B4 AA AA AA B4 B4 B4 0D
# 0A B4 B4 B4 B4 B4 B4 B4 B4 B4 B4 B4 B4 B4 B4 0D
