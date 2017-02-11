# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import wiringpi as wp
import time
import struct

SPI_SPEED = 1000000
SOLENOID_PIN = 11

class Commands:
    def __init__(self):
        self.solenoid_state = False
        self.x = 0
        self.y = 0
        self.setup()
    def setup(self):
        wp.wiringPiSPISetup(0, SPI_SPEED)
        wp.wiringPiSPISetup(1, SPI_SPEED)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(16, GPIO.IN)
        GPIO.setup(18, GPIO.IN)
        GPIO.setup(SOLENOID_PIN, GPIO.OUT)
        set_acc(0xFFF)
        set_dec(0xFFF)
        set_maxspeed(0x20)
        set_minspeed(0x00)
        set_kvalhold(0xFF)
        set_kvalacc(0xFF)
        set_kvaldec(0xFF)
        set_kvalrun(0xFF)
        set_stallth(0x7F)
        set_ocdth(0x0F)
        set_stepmode(0x07)
    def move(self, step, channel):
        print(step, channel)
        _move(step, channel)
        if not channel:
            self.x += step
        else:
            self.y += step
    def mov2(self, step, channel):
        dir = step / abs(step)
	for i in range(abs(step)):
	    _move(dir, channel)
	    time.sleep(0.0001)
    def solenoid(self):
        self.solenoid_state = not self.solenoid_state
        GPIO.output(SOLENOID_PIN, self.solenoid_state)
    def solenoid2(self, v):
        self.solenoid_state = v
        GPIO.output(SOLENOID_PIN, self.solenoid_state)
    def reset(self):
        self.solenoid_state = True
        self.solenoid()
        gohome()
    def moveRoute(self, route):
        # route = [ [x1, y1], [x2, y2],...]
        for pos in route:
            for i in range(2):
                self.move(pos[i], i)
            for i in range(2):
                busydelay(0.2, i)
                if pos[i] <= 25000:
                    busydelay(0.1, i)
                elif pos[i] <= 50000:
                    busydelay(0.2, i)
                elif pos[i] <= 100000:
                    busydelay(0.3, i)
                else:
                    busydelay(0.4, i)
    def moveTo(self, x, y):
        self.move(x, 0)
        time.sleep(0.2)
        self.move(y, 1)
        time.sleep(0.2)
    def tap(self, t):
        self.solenoid_state = False
        self.solenoid()
        time.sleep(t)
        self.solenoid()
def write(data, channel):
    data = struct.pack('B', data)
    if channel == 0:
        while not GPIO.input(16):
            pass
    else:
        while not GPIO.input(18):
            pass
    wp.wiringPiSPIDataRW(channel, data)

def set_acc(data):
    data_m = (0x0F00 & data) >> 8
    data_l = (0x00FF & data)

    write(0x05, 0)
    write(data_m, 0)
    write(data_l, 0)

    write(0x05, 1)
    write(data_m, 1)
    write(data_l, 1)

def set_dec(data):
    data_m = (0x0F00 & data) >> 8
    data_l = (0x00FF & data)

    write(0x06, 0)
    write(data_m, 0)
    write(data_l, 0)

    write(0x06, 1)
    write(data_m, 1)
    write(data_l, 1)

def set_maxspeed(data):
    data_m = (0x0300 & data) >> 8
    data_l = (0x00FF & data)

    write(0x07, 0)
    write(data_m, 0)
    write(data_l, 0)

    write(0x07, 1)
    write(data_m, 1)
    write(data_l, 1)

def set_minspeed(data):
    data_m = (0x0300 & data) >> 8
    data_l = (0x00FF & data)

    write(0x08, 0)
    write(data_m, 0)
    write(data_l, 0)

    write(0x08, 1)
    write(data_m, 1)
    write(data_l, 1)

def set_kvalhold(data):
    write(0x09, 0)
    write(data, 0)

    write(0x09, 1)
    write(data, 1)

def set_kvalrun(data):
    write(0x0A, 0)
    write(data, 0)

    write(0x0A, 1)
    write(data, 1)

def set_kvalacc(data):
    write(0x0B, 0)
    write(data, 0)

    write(0x0B, 1)
    write(data, 1)

def set_kvaldec(data):
    write(0x0C, 0)
    write(data, 0)

    write(0x0C, 1)
    write(data, 1)

def set_ocdth(data):
    write(0x13, 0)
    write(data, 0)

    write(0x13, 1)
    write(data, 1)
def set_stallth(data):
    write(0x14, 0)
    write(data, 0)

    write(0x14, 1)
    write(data, 1)

def set_stepmode(data):
    write(0x16, 0)
    write(data, 0)

    write(0x16, 1)
    write(data, 1)

#----------------------------------------------

def run(speed, channel):
    if speed < 0:
        com = 0x50
        speed = -1 * speed
    else:
        com = 0x51

    speed_h = (0x0F0000 & speed) >> 16
    speed_m = (0x00FF00 & speed) >> 8
    speed_l = (0x00FF & speed)

    write(com, channel)
    write(speed_h, channel)
    write(speed_m, channel)
    write(speed_l, channel)

def _move(step, channel):
    if step < 0:
        com = 0x40
        step = -1 * step
    else:
        com = 0x41

    step_h = (0xFF0000 & step) >> 16
    step_m = (0x00FF00 & step) >> 8
    step_l = (0x00FF & step)

    write(com, channel)
    write(step_h, channel)
    write(step_m, channel)
    write(step_l, channel)

def goto(pos, channel):
    if pos < 0:
        com = 0x68
    else:
        com = 0x69

    pos_h = (0x3F0000 & pos) >> 16
    pos_m = (0x00FF00 & pos) >> 8
    pos_l = (0x0000FF & pos)

    write(com, channel)
    write(pos_h, channel)
    write(pos_m, channel)
    write(pos_l, channel)

def gohome():
    com = 0x70
    write(com, 0)
    write(com, 1)

def resetpos():
    com = 0xD8
    write(com, 0)
    write(com, 1)

def soft_stop(channel):
    com = 0xB0
    write(com, channel)

def hard_stop(channel):
    com = 0xB8
    write(com, channel)

def soft_hiz(channel):
    com = 0xA0
    write(com, channel)

def hard_hiz(channel):
    com = 0xA8
    write(com, channel)

def busydelay(t, channel):
    if channel == 0:
        while not GPIO.input(16):
            pass
    else:
        while not GPIO.input(18):
            pass

    time.sleep(t)
