import pygame
from pygame.locals import *
from PIL import Image
from sys import exit
import math
import struct
import serial
import time
import copy


def make_bg():
    bg_pic = Image.open('reset.png').resize((100, 50))
    bg_pic = bg_pic.convert('RGBA')
    bg_pic.putalpha(alpha=5)
    bg_pic.save("reset.png")


SLEEP_TIME = 1.3
LAST_TIME = time.time()
pi = 3.1415926535
bgp = 'aa.png'
dgp = 'b.png'
pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)
background = pygame.image.load(bgp).convert_alpha()
# work_rect = pygame.image.load(dgp).convert_alpha()
reset = pygame.image.load('reset.png').convert_alpha()
clear = pygame.image.load('clear.png').convert_alpha()
work_rect = pygame.draw.rect(background, (255, 255, 255, 200), (40, 40, 450, 400))
angles = [0, 0, 0, 0, 0, 0]
Fullscreen = False
L = 60
points_vectors = [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]]
colors = [(30, 10, 100), (60, 50, 100), (90, 100, 100), (120, 150, 100), (150, 200, 100), (180, 255, 100)]
choose = 0
choose_now = choose
key_flag = 0
go_reset_flag = 0
da = 0.001
send_history = []
angle_history = []
send_index = 0
color_work_rect = Color(255, 255, 255, 150)
velocity = 0
vel_rect_x = 80

#ser = serial.Serial("COM3", 9600)


def get_lines():
    solute_angle = 0
    for i, angle in enumerate(angles):
        solute_angle = angle + solute_angle
        points_vectors[i][0] = L * math.cos(solute_angle)
        points_vectors[i][1] = L * math.sin(solute_angle)


def show_vel():
    global vel_rect_x
    vel_rect_x = vel_rect_x + velocity
    pygame.draw.rect(background, (0, 255, 255, 255), (vel_rect_x, 360, 40, 40))
    if vel_rect_x > 410 and velocity > 0:
        vel_rect_x = 40
    if vel_rect_x < 40 and velocity < 0:
        vel_rect_x = 410


def show_lines(choose):
    last_x = 70
    last_y = 200
    rects = []
    pygame.draw.rect(background, color_work_rect, (40, 40, 450, 400))
    for i, vector in enumerate(points_vectors):
        if i == choose:
            rect = pygame.draw.line(background, (255, 0, 0), (last_x, last_y),
                                    (last_x + vector[0], last_y + vector[1]), 30)
            rects.append(rect)
            last_x, last_y = last_x + vector[0], last_y + vector[1]
        else:
            rect = pygame.draw.line(background, colors[i], (last_x, last_y),
                                    (last_x + vector[0], last_y + vector[1]), 30)
            rects.append(rect)
            last_x, last_y = last_x + vector[0], last_y + vector[1]

    return rects


def send_messages():
    global LAST_TIME
    send_angle = [0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0x00, 0x00, 0xdd]
    if time.time() - LAST_TIME > SLEEP_TIME:
        for i in range(6):
            send_angle[2 * i + 2] = int(angles[i] * 180 / pi + 180)
        print velocity
        if velocity == 0:
            send_angle[13] = 180
        else:
            send_angle[13] = int(1 / (velocity) + 180)
        send_byte = struct.pack('16B', *send_angle)
        send_history.append(send_angle)
        angle_history.append(copy.deepcopy(angles))
        #ser.write(send_byte)
        print(send_angle, send_byte)
        LAST_TIME = time.time()


def init():
    global send_angle, points_vectors, angles, go_reset_flag, send_history, velocity, vel_rect_x
    # points_vectors = [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]]
    angles = [0, 0, 0, 0, 0, 0]
    go_reset_flag = 0
    send_history = []
    velocity = 0
    vel_rect_x = 80


def f_reset():
    global LAST_TIME, send_index, angles, go_reset_flag, velocity
    if go_reset_flag == 1:
        print("IIIIIIIIIIII AM REVERSE!!")
        send_history.reverse()
        angle_history.reverse()
        go_reset_flag = 2
    if time.time() - LAST_TIME > SLEEP_TIME:
        # print send_history[send_index:len(send_history)]
        print angle_history[send_index:len(angle_history)]
        print "go_back!"
        if send_index < len(send_history):
            send_angle = send_history[send_index]
            send_angle[13] = 180 - (send_angle[13] - 180)
            velocity = 1.0 / (send_angle[13] - 180) if send_angle[13] != 180 else 0
            angles = angle_history[send_index]
            send_byte = struct.pack('16B', *send_angle)
            #ser.write(send_byte)
            print(send_byte)
        else:
            print("send history is none!!")
            init()

        send_index = send_index + 1
        LAST_TIME = time.time()
        print angles


while True:
    screen.set_clip((0, 0, 640, 480))
    background_rect = screen.blit(background, (0, 0))
    reset_rect = screen.blit(reset, (490, 120))
    clear_rect = screen.blit(clear, (490, 240))
    get_lines()
    rects = show_lines(choose)
    show_vel()

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    if event.type == MOUSEBUTTONDOWN:
        mouse_pos_down = pygame.mouse.get_pos()
        for i, rect in enumerate(rects):
            if rect.collidepoint(mouse_pos_down):
                choose = i
        if reset_rect.collidepoint(mouse_pos_down) and go_reset_flag == 0:
            go_reset_flag = 1
            f_reset()
        if clear_rect.collidepoint(mouse_pos_down):
            print("send history is cleared!!")
            init()

    if event.type == KEYDOWN:
        if event.key == K_UP:
            angles[choose] -= da
        if event.key == K_DOWN:
            angles[choose] += da

        if event.key == K_LEFT and key_flag == 0:
            key_flag = 1
            choose -= 1

        if event.key == K_RIGHT and key_flag == 0:
            key_flag = 1
            choose += 1

        if event.key == K_a:
            velocity -= 0.005
        if event.key == K_d:
            velocity += 0.005
        if event.key == K_s:
            velocity = 0

        if event.key == K_f:
            Fullscreen = not Fullscreen
            if Fullscreen:
                screen = pygame.display.set_mode((640, 480), FULLSCREEN, 32)
            else:
                screen = pygame.display.set_mode((640, 480), 0, 32)
    if event.type == KEYUP:
        key_flag = 0

    if go_reset_flag:
        f_reset()
    else:
        send_messages()

    pygame.display.update()
