import pygame
from pygame.locals import *
from PIL import Image
from sys import exit
import math
import struct
import serial
import time
import copy

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


def make_bg():
    bg_pic = Image.open('reset.png').resize((100, 50))
    bg_pic = bg_pic.convert('RGBA')
    bg_pic.putalpha(alpha=5)
    bg_pic.save("reset.png")


class lines():
    angles = [0, 0, 0, 0, 0, 0]
    points_vectors = [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]]
    colors = [(30, 10, 100), (60, 50, 100), (90, 100, 100), (120, 150, 100), (150, 200, 100), (180, 255, 100)]
    last_x = 70
    last_y = 200
    L = 60

    def get_line(self):
        solute_angle = 0
        for i, angle in enumerate(self.angles):
            solute_angle = angle + solute_angle
            self.points_vectors[i][0] = self.L * math.cos(solute_angle)
            self.points_vectors[i][1] = self.L * math.sin(solute_angle)

    def show_line(self, choose):
        global background
        last_x = self.last_x
        last_y = self.last_y
        self.get_line()
        rects = []
        for i, vector in enumerate(self.points_vectors):
            if i == choose:
                rect = pygame.draw.line(background, (255, 0, 0), (last_x, last_y),
                                        (last_x + vector[0], last_y + vector[1]), 30)
                rects.append(rect)
                last_x, last_y = last_x + vector[0], last_y + vector[1]
            else:
                rect = pygame.draw.line(background, self.colors[i], (last_x, last_y),
                                        (last_x + vector[0], last_y + vector[1]), 30)
                rects.append(rect)
                last_x, last_y = last_x + vector[0], last_y + vector[1]

    def line_init(self):
        self.angles = [0, 0, 0, 0, 0, 0]

    def __init__(self, x, y):
        self.last_x = x
        self.last_y = y


class control_pygame_show():
    lines_x = lines(70, 200)
    lines_y = lines(70, 400)
    vel_rect_x = 80
    velocity = 0

    send_history = []
    angle_history = []
    send_index = 0
    #ser = serial.Serial("COM3", 9600)
    SLEEP_TIME = 1.3
    LAST_TIME = time.time()
    go_reset_flag = 0
    choose_x = 0
    choose_y = 0

    def show_vel(self):
        global  background
        self.vel_rect_x = self.vel_rect_x + self.velocity
        pygame.draw.rect(background, (0, 255, 255, 255), (self.vel_rect_x, 360, 40, 40))
        if self.vel_rect_x > 410 and self.velocity > 0:
            self.vel_rect_x = 40
        if self.vel_rect_x < 40 and self.velocity < 0:
            self.vel_rect_x = 410

    def show_lines(self):
        #pygame.draw.rect(background, (255, 255, 255, 150), (40, 40, 450, 400))
        self.lines_x.show_line(self.choose_x)
        self.lines_y.show_line(self.choose_y)

    def send_messages(self):
        send_angle = [0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0x00, 0x00, 0xdd]
        if time.time() - self.LAST_TIME > self.SLEEP_TIME:
            for i in range(6):
                send_angle[2 * i + 2] = int(self.lines_x.angles[i] * 180 / pi + 180)

            for i in range(6):
                send_angle[2 * i + 1] = int(self.lines_y.angles[i] * 180 / pi + 180)

            print self.velocity
            if self.velocity == 0:
                send_angle[13] = 180
            else:
                send_angle[13] = int(1 / self.velocity + 180)
            send_byte = struct.pack('16B', *send_angle)
            self.send_history.append(send_angle)
            self.angle_history.append((copy.deepcopy(self.lines_x.angles), copy.deepcopy(self.lines_y.angles)))
            #self.ser.write(send_byte)
            print(send_angle, send_byte)
            self.LAST_TIME = time.time()

    def f_reset(self):
        if self.go_reset_flag == 1:
            print("IIIIIIIIIIII AM REVERSE!!")
            self.send_history.reverse()
            self.angle_history.reverse()
            self.go_reset_flag = 2
        if time.time() - self.LAST_TIME > self.SLEEP_TIME:
            # print send_history[send_index:len(send_history)]
            print self.angle_history[self.send_index:len(self.angle_history)]
            print "go_back!"
            if self.send_index < len(self.send_history):
                send_angle = self.send_history[self.send_index]
                send_angle[13] = 180 - (send_angle[13] - 180)
                self.velocity = 1.0 / (send_angle[13] - 180) if send_angle[13] != 180 else 0
                self.lines_x.angles, self.lines_y.angles = self.angle_history[self.send_index]
                send_byte = struct.pack('16B', *send_angle)
              #  self.ser.write(send_byte)
                print(send_byte)
            else:
                print("send history is none!!")
                self.show_init()
            self.send_index = self.send_index + 1
            self.LAST_TIME = time.time()

    def show_init(self):
        self.lines_x.line_init()
        self.lines_y.line_init()
        self.go_reset_flag = 0
        self.send_history = []
        self.velocity = 0
        self.vel_rect_x = 80

    def pygame_show(self):
        global screen,background,reset,clear
        Fullscreen = False
        key_flag_x = 0
        key_flag_y = 0
        da = 0.001
        while True:
            screen.blit(background, (0, 0))
            reset_rect = screen.blit(reset, (490, 120))
            clear_rect = screen.blit(clear, (490, 240))
            pygame.draw.rect(background, (255, 255, 255, 150), (40, 40, 450, 400))
            self.show_lines()
            self.show_vel()

            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos_down = pygame.mouse.get_pos()
                # for i, rect in enumerate(rects):
                #     if rect.collidepoint(mouse_pos_down):
                #         choose = i
                if reset_rect.collidepoint(mouse_pos_down) and self.go_reset_flag == 0:
                    self.go_reset_flag = 1
                    self.f_reset()
                if clear_rect.collidepoint(mouse_pos_down):
                    print("send history is cleared!!")
                    self.show_init()

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.lines_y.angles[self.choose_y] -= da
                if event.key == K_DOWN:
                    self.lines_y.angles[self.choose_y] += da
                if event.key == K_i:
                    self.lines_x.angles[self.choose_x] -= da
                if event.key == K_k:
                    self.lines_x.angles[self.choose_x] += da

                if event.key == K_LEFT and key_flag_y == 0:
                    key_flag_y = 1
                    self.choose_x -= 1
                if event.key == K_RIGHT and key_flag_y == 0:
                    key_flag_y = 1
                    self.choose_y += 1
                if event.key == K_j and key_flag_x == 0:
                    key_flag_x = 1
                    self.choose_x -= 1
                if event.key == K_l and key_flag_x == 0:
                    key_flag_x = 1
                    self.choose_x += 1

                if event.key == K_a:
                    self.velocity -= 0.005
                if event.key == K_d:
                    self.velocity += 0.005
                if event.key == K_s:
                    self.velocity = 0

                if event.key == K_f:
                    Fullscreen = not Fullscreen
                    if Fullscreen:
                        screen = pygame.display.set_mode((640, 480), FULLSCREEN, 32)
                    else:
                        screen = pygame.display.set_mode((640, 480), 0, 32)

            if event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    key_flag_y = 0

                if event.key == K_j or event.key == K_l:
                    key_flag_x = 0

            if self.go_reset_flag:
                self.f_reset()
            else:
                self.send_messages()

            pygame.display.update()


a=control_pygame_show()
a.pygame_show()