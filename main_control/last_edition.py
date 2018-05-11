import pygame
from pygame.locals import *
from PIL import Image
from sys import exit
import math
import struct
import serial
import time
import copy
import xlwt
import xlrd

pi = 3.1415926535
bgp = 'aa.jpg'
dgp = 'b.png'
pygame.init()
screen = pygame.display.set_mode((960, 720), 0, 32)
background = pygame.image.load(bgp).convert_alpha()
reset = pygame.image.load('reset.png').convert_alpha()
clear = pygame.image.load('clear.png').convert_alpha()
follow_head = pygame.image.load('follow_head.png').convert_alpha()
handle = pygame.image.load('handle.png').convert_alpha()
load_excel = pygame.image.load('load_excel.png').convert_alpha()
work_rect = pygame.draw.rect(background, (255, 255, 255, 200), (40, 40, 450, 400))
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('test', cell_overwrite_ok=True)
sheet_index = 0


def make_bg():
    bg_pic = Image.open('a.jpg').resize((960, 720))
    bg_pic = bg_pic.convert('RGBA')
    bg_pic.putalpha(alpha=5)
    bg_pic.save("aa.png")


class lines():
    colors = [(30, 10, 100), (60, 50, 100), (90, 100, 100), (120, 150, 100), (150, 200, 100), (180, 255, 100)]
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
        self.angles = [0, 0, 0, 0, 0, 0]
        self.points_vectors = [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]]


class control_pygame_show():
    vel_rect_x = 80
    velocity = 0
    send_index = 0
    #ser = serial.Serial("COM3", 9600)
    SLEEP_TIME = 1
    LAST_TIME = time.time()
    send_history = []
    angle_history = []
    time_history = []
    go_reset_flag = 0
    choose = 0
    xls_flag = 0
    follow_head_flag = 0
    change_angle_flag = 0
    send_messages_flag = 0
    follow_flag = 0
    xls_go_flag = 0
    change_daogui_flag = 0
    excel_index = 21

    def __init__(self):
        self.lines_x = lines(150, 230)
        self.lines_y = lines(150, 430)
        self.follow_a = 0  # left_right,first,x
        self.follow_c = 0  # up_down,second,y
        self.last_follow_angle = [0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0x00, 0x00, 0xdd]
        self.last_follow_line_x = copy.deepcopy(self.lines_x.angles)
        self.last_follow_line_y = copy.deepcopy(self.lines_y.angles)
        self.send_angle = [0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0x00, 0x00, 0xdd]

    def show_vel(self):
        global background
        self.vel_rect_x = self.vel_rect_x + self.velocity
        pygame.draw.rect(background, (0, 255, 255, 255), (self.vel_rect_x, 600, 40, 40))
        if self.vel_rect_x > 410 and self.velocity > 0:
            self.vel_rect_x = 40
        if self.vel_rect_x < 40 and self.velocity < 0:
            self.vel_rect_x = 410

    def show_lines(self):
        # pygame.draw.rect(background, (255, 255, 255, 150), (40, 40, 450, 400))
        self.lines_x.show_line(self.choose)
        self.lines_y.show_line(self.choose)

    def let_daogui_go(self):
        global sheet, sheet_index
        if self.velocity == 0:
            self.send_angle[13] = 180
        else:
            self.send_angle[13] = int(1 / self.velocity + 180)
        send_byte = struct.pack('16B', *self.send_angle)
        sheet.write(sheet_index, 0, str(self.send_angle))
        sheet.write(sheet_index, 1, str(copy.deepcopy(self.lines_x.angles)))
        sheet.write(sheet_index, 2, str(copy.deepcopy(self.lines_y.angles)))
        self.send_history.append(copy.deepcopy(self.send_angle))
        self.angle_history.append((copy.deepcopy(self.lines_x.angles), copy.deepcopy(self.lines_y.angles)))
        self.last_follow_line_x = copy.deepcopy(self.lines_x.angles)
        self.last_follow_line_y = copy.deepcopy(self.lines_y.angles)
        self.last_follow_angle = copy.deepcopy(self.send_angle)
        #self.ser.write(send_byte)
        self.time_history.append(time.time() - self.LAST_TIME)
        sheet.write(sheet_index, 3, time.time() - self.LAST_TIME)
        print(self.send_angle, send_byte, time.time() - self.LAST_TIME)
        sheet_index += 1
        self.LAST_TIME = time.time()

    def only_head(self):
        global sheet_index, sheet
        self.send_angle[11] = int(self.follow_a * 180 / pi + 180)
        self.send_angle[12] = int(self.follow_c * 180 / pi + 180)
        self.lines_y.angles[5] = self.follow_a
        self.lines_x.angles[5] = self.follow_c
        if self.velocity == 0:
            self.send_angle[13] = 180
        else:
            self.send_angle[13] = int(1 / self.velocity + 180)
        send_byte = struct.pack('16B', *self.send_angle)
        sheet.write(sheet_index, 0, str(self.send_angle))
        sheet.write(sheet_index, 1, str(copy.deepcopy(self.lines_x.angles)))
        sheet.write(sheet_index, 2, str(copy.deepcopy(self.lines_y.angles)))
        self.send_history.append(copy.deepcopy(self.send_angle))
        self.angle_history.append((copy.deepcopy(self.lines_x.angles), copy.deepcopy(self.lines_y.angles)))
        self.last_follow_line_x = copy.deepcopy(self.lines_x.angles)
        self.last_follow_line_y = copy.deepcopy(self.lines_y.angles)
        self.last_follow_angle = copy.deepcopy(self.send_angle)
        #self.ser.write(send_byte)

        self.time_history.append(time.time() - self.LAST_TIME)
        sheet.write(sheet_index, 3, time.time() - self.LAST_TIME)
        print(self.send_angle, send_byte, time.time() - self.LAST_TIME)
        sheet_index += 1
        self.LAST_TIME = time.time()

    def follow_reset(self):
        if self.go_reset_flag == 1:
            print("followwwwwwwwwwwwww AM REVERSE!!")
            self.send_history.reverse()
            self.angle_history.reverse()
            self.time_history.reverse()
            self.time_history = [1.0] + self.time_history
            self.angle_history = copy.deepcopy(
                self.angle_history + [([0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0])])
            self.send_history = copy.deepcopy(
                self.send_history + [[0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0, 0xdd]])
            print "---------------", len(self.send_history), len(self.angle_history), len(
                self.time_history), "-----------------------"
            self.go_reset_flag = 2
            self.LAST_TIME = time.time()
        if self.send_index < len(self.send_history):
            if time.time() - self.LAST_TIME > self.time_history[self.send_index]:
                print "go_back!"
                self.send_angle = copy.deepcopy(self.send_history[self.send_index])
                self.send_angle[13] = 180 - (self.send_angle[13] - 180)
                self.velocity = 1.0 / (self.send_angle[13] - 180) if self.send_angle[13] != 180 else 0
                self.lines_x.angles, self.lines_y.angles = copy.deepcopy(self.angle_history[self.send_index])
                send_byte = struct.pack('16B', *self.send_angle)
                #self.ser.write(send_byte)
                print(self.send_angle, self.time_history[self.send_index])
                self.send_index = self.send_index + 1
                self.LAST_TIME = time.time()
        else:
            print("FOLLOW RESET  send history is none!!")
            self.send_index = 0
            self.go_reset_flag = 0

    def xls_go(self):
        if self.send_index < len(self.send_history):
            if time.time() - self.LAST_TIME > self.time_history[self.send_index]:
                print "XLS GO!"
                self.send_angle = copy.deepcopy(self.send_history[self.send_index])
                self.velocity = 1.0 / (self.send_angle[13] - 180) if self.send_angle[13] != 180 else 0
                self.lines_x.angles, self.lines_y.angles = copy.deepcopy(self.angle_history[self.send_index])
                send_byte = struct.pack('16B', *self.send_angle)
                #self.ser.write(send_byte)
                print(self.send_angle, self.time_history[self.send_index])
                self.send_index = self.send_index + 1
                self.LAST_TIME = time.time()
        else:
            print("GO RESET  send history is none!!")
            self.send_index = 0
            self.xls_go_flag = 0
            # self.go_reset_flag = 1

    def follow_the_head(self):
        global sheet_index, sheet
        self.send_angle = copy.deepcopy(self.last_follow_angle)
        print "follow now!!"
        self.send_angle[11] = int(self.follow_a * 180 / pi + 180)
        self.send_angle[12] = int(self.follow_c * 180 / pi + 180)
        self.lines_y.angles[5] = self.follow_a
        self.lines_x.angles[5] = self.follow_c
        for i in range(5):
            self.send_angle[-2 * i + 9] = self.last_follow_angle[-2 * i + 11]
            self.send_angle[-2 * i + 10] = self.last_follow_angle[-2 * i + 12]
            self.lines_x.angles[-i + 4] = self.last_follow_line_x[-i + 5]
            self.lines_y.angles[-i + 4] = self.last_follow_line_y[-i + 5]
        print self.last_follow_angle, self.send_angle
        print self.last_follow_line_y, self.lines_y
        if self.velocity == 0:
            self.send_angle[13] = 180
        else:
            self.send_angle[13] = int(1 / self.velocity + 180)
        send_byte = struct.pack('16B', *self.send_angle)
        sheet.write(sheet_index, 0, str(self.send_angle))
        sheet.write(sheet_index, 1, str(copy.deepcopy(self.lines_x.angles)))
        sheet.write(sheet_index, 2, str(copy.deepcopy(self.lines_y.angles)))

        self.send_history.append(self.send_angle)
        self.angle_history.append((copy.deepcopy(self.lines_x.angles), copy.deepcopy(self.lines_y.angles)))
        self.last_follow_line_x = copy.deepcopy(self.lines_x.angles)
        self.last_follow_line_y = copy.deepcopy(self.lines_y.angles)
        self.last_follow_angle = copy.deepcopy(self.send_angle)
        #self.ser.write(send_byte)
        self.time_history.append(time.time() - self.LAST_TIME)
        sheet.write(sheet_index, 3, time.time() - self.LAST_TIME)
        sheet_index += 1
        print(self.send_angle, send_byte, time.time() - self.LAST_TIME)
        self.LAST_TIME = time.time()

    def send_messages(self):
        global sheet, sheet_index
        self.send_angle = [0xbb, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 0x00, 0x00, 0xdd]
        if time.time() - self.LAST_TIME > self.SLEEP_TIME:
            print self.lines_x.angles, self.lines_y.angles
            for i in range(6):
                self.send_angle[2 * i + 2] = int(self.lines_x.angles[i] * 180 / pi + 180)

            for i in range(6):
                self.send_angle[2 * i + 1] = int(self.lines_y.angles[i] * 180 / pi + 180)

            print self.velocity
            if self.velocity == 0:
                self.send_angle[13] = 180
            else:
                self.send_angle[13] = int(1 / self.velocity + 180)
            send_byte = struct.pack('16B', *self.send_angle)
            # sheet.write(sheet_index, 0, str(self.send_angle))
            # sheet.write(sheet_index, 1, str(copy.deepcopy(self.lines_x.angles)))
            # sheet.write(sheet_index, 2, str(copy.deepcopy(self.lines_y.angles)))
            # sheet_index += 1
            self.send_history.append(self.send_angle)
            self.angle_history.append((copy.deepcopy(self.lines_x.angles), copy.deepcopy(self.lines_y.angles)))
            #self.ser.write(send_byte)
            print(self.send_angle, send_byte)
            self.LAST_TIME = time.time()

    def f_reset(self):
        if self.go_reset_flag == 1:
            print("IIIIIIIIIIII AM REVERSE!!")
            self.send_history.reverse()
            self.angle_history.reverse()
            if self.follow_head_flag == 1:
                pass
            else:
                self.make_history_data()
            self.go_reset_flag = 2
        if time.time() - self.LAST_TIME > self.SLEEP_TIME:
            print self.send_history[self.send_index:len(self.send_history)]
            print self.angle_history[self.send_index:len(self.angle_history)]
            print "go_back!"
            if self.send_index < len(self.send_history):
                self.send_angle = copy.deepcopy(self.send_history[self.send_index])
                self.send_angle[13] = 180 - (self.send_angle[13] - 180)
                self.velocity = 1.0 / (self.send_angle[13] - 180) if self.send_angle[13] != 180 else 0
                self.lines_x.angles, self.lines_y.angles = copy.deepcopy(self.angle_history[self.send_index])
                send_byte = struct.pack('16B', *self.send_angle)
                #self.ser.write(send_byte)
                print(self.send_angle)
            else:
                print("send history is none!!")
                self.show_init()
            self.send_index = self.send_index + 1
            self.LAST_TIME = time.time()

    def make_history_data(self):
        datas = copy.deepcopy(self.send_history)
        data_history = 0
        data_times = 0
        for i, data in enumerate(datas):
            if data == data_history:
                data_times += 1
                if data_times > 1:
                    self.send_history[i] = 0
                    self.angle_history[i] = 0
            else:
                data_times = 0
            data_history = data
        while 0 in self.send_history:
            self.send_history.remove(0)
        while 0 in self.angle_history:
            self.angle_history.remove(0)
        print "---------------------", self.send_history
        print self.angle_history

    def go_from_excel(self, num):
        txt = 'history' + str(num) + '.xls'
        data = xlrd.open_workbook(txt)
        sheet = data.sheets()[0]
        rows = sheet.nrows
        text0 = []
        text1 = []
        text2 = []
        text3 = []
        for i in range(rows):
            text = sheet.row_values(i)[0][1:-1].split(',')
            for x, t in enumerate(text):
                text[x] = int(t)
            text0.append(text)
        for i in range(rows):
            text = sheet.row_values(i)[1][1:-1].split(',')
            for x, t in enumerate(text):
                text[x] = float(t)
            text1.append(text)
        for i in range(rows):
            text = sheet.row_values(i)[2][1:-1].split(',')
            for x, t in enumerate(text):
                text[x] = float(t)
            text2.append(text)
        for i in range(rows):
            text = sheet.row_values(i)[3]
            text3.append(text)
        self.send_history = text0
        self.angle_history = zip(text1, text2)
        self.time_history = text3
        # self.send_history.reverse()
        # self.angle_history.reverse()
        # self.time_history.reverse()
        # self.send_history = copy.deepcopy(text0 + self.send_history)
        # self.angle_history = copy.deepcopy(zip(text1, text2) + self.angle_history)
        # self.time_history = copy.deepcopy(text3 + self.time_history)
        # print self.send_history
        # print self.angle_history
        # print self.time_history
        # self.send_history.reverse()
        # self.angle_history.reverse()
        # self.time_history.reverse()
        print "**************", len(self.angle_history), len(self.send_history), len(self.time_history), "************"
        self.xls_go_flag = 1

    def show_init(self):
        self.lines_x.line_init()
        self.lines_y.line_init()
        self.go_reset_flag = 0
        self.send_history = []
        self.send_index = 0
        self.velocity = 0
        self.vel_rect_x = 80

    def pygame_show(self):
        global screen, background, reset, clear, book, sheet_index
        Fullscreen = False
        key_flag = 0
        da = 0.05
        da1 = 0.05
        while True:
            screen.blit(background, (0, 0))
            reset_rect = screen.blit(reset, (750, 50))
            clear_rect = screen.blit(clear, (750, 170))
            xls_rect = screen.blit(load_excel, (750, 290))
            follow_head_rect = screen.blit(follow_head, (750, 410))
            send_messages_rect = screen.blit(handle,  (750, 530))
            pygame.draw.rect(background, (255, 255, 255, 150), (40, 40, 650, 640))
            self.show_lines()
            self.show_vel()
            if self.go_reset_flag:
                #self.follow_reset()
                self.f_reset()
            elif self.follow_head_flag:
                # self.let_daogui_go()
                pass
            elif self.xls_go_flag:
                self.xls_go()
            elif self.send_messages_flag:
                self.send_messages()

            for event in pygame.event.get():
                if event.type == QUIT:
                    txt = 'history' + str(sheet_index) + '.xls'
                    book.save(txt)
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos_down = pygame.mouse.get_pos()
                    # for i, rect in enumerate(rects):
                    #     if rect.collidepoint(mouse_pos_down):
                    #         choose = i
                    if reset_rect.collidepoint(mouse_pos_down) and self.go_reset_flag == 0:
                        self.go_reset_flag = 1
                    if clear_rect.collidepoint(mouse_pos_down):
                        print("send history is cleared!!")
                        self.show_init()
                    if xls_rect.collidepoint(mouse_pos_down):
                        print("go_from_excel!!")
                        self.go_from_excel(self.excel_index)
                    if follow_head_rect.collidepoint(mouse_pos_down):
                        print("follow_head!!")
                        self.follow_head_flag = 1
                        self.angle_history = []
                        self.send_history = []
                    if send_messages_rect.collidepoint(mouse_pos_down):
                        self.send_messages_flag = 1

                if event.type == KEYDOWN:
                    if self.follow_head_flag == 1:
                        if event.key == K_SPACE and self.follow_flag == 0:
                            self.follow_flag = 1
                            self.follow_a = 0
                            self.follow_c = 0
                            self.follow_the_head()

                        if (
                                                event.key == K_a or event.key == K_s or event.key == K_d or event.key == K_w) and self.change_angle_flag == 0:
                            self.change_angle_flag = 1
                            if event.key == K_a:
                                self.follow_a += da1
                            elif event.key == K_d:
                                self.follow_a -= da1
                            elif event.key == K_s:
                                self.follow_c += da1
                            elif event.key == K_w:
                                self.follow_c -= da1
                            self.only_head()
                        if (
                                            event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN) and self.change_daogui_flag == 0:
                            self.change_daogui_flag = 1
                            if event.key == K_LEFT:
                                self.velocity -= 0.1
                            if event.key == K_RIGHT:
                                self.velocity += 0.1
                            if event.key == K_DOWN:
                                self.velocity = 0
                            self.let_daogui_go()


                    else:

                        if event.key == K_a:
                            self.lines_y.angles[self.choose] += da
                        if event.key == K_d:
                            self.lines_y.angles[self.choose] -= da
                        if event.key == K_s:
                            self.lines_x.angles[self.choose] += da
                        if event.key == K_w:
                            self.lines_x.angles[self.choose] -= da

                        if (
                                            event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN) and self.change_daogui_flag == 0:
                            self.change_daogui_flag = 1
                            if event.key == K_LEFT:
                                self.velocity -= 0.1
                            if event.key == K_RIGHT:
                                self.velocity += 0.1
                            if event.key == K_DOWN:
                                self.velocity = 0

                    if event.key == K_UP and key_flag == 0:
                        key_flag = 1
                        if self.choose == 0:
                            self.choose = 6
                        self.choose -= 1

                    if event.key == K_f:
                        Fullscreen = not Fullscreen
                        if Fullscreen:
                            screen = pygame.display.set_mode((640, 480), FULLSCREEN, 32)
                        else:
                            screen = pygame.display.set_mode((640, 480), 0, 32)

                if event.type == KEYUP:
                    if event.key == K_UP:
                        key_flag = 0
                    if (
                                            event.key == K_a or event.key == K_s or event.key == K_d or event.key == K_w) and self.change_angle_flag == 1:
                        self.change_angle_flag = 0
                    if (
                                        event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN) and self.change_daogui_flag == 1:
                        self.change_daogui_flag = 0
                    if event.key == K_SPACE:
                        self.follow_flag = 0
            pygame.display.update()


a = control_pygame_show()
a.pygame_show()
