# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 00:42:19 2020

@author: User
"""
import RPi.GPIO as GPIO
import time as t
class sasGPIO:
    def __init__(self, locationType):
        self.redLightPin = 21
        self.greenLightPin = 20
        self.blueLightPin = 13
        self.buzzerPin = 27
        self.doorLockPin = 26
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.redLightPin, GPIO.OUT)
        GPIO.setup(self.greenLightPin, GPIO.OUT)
        GPIO.setup(self.blueLightPin, GPIO.OUT)
        GPIO.setup(self.buzzerPin, GPIO.OUT)
        GPIO.setup(self.doorLockPin, GPIO.OUT)
        
    def turnLEDON(self, color):
        print("Requested Color: {}".format(color))
        if color == 'R':
            GPIO.output(self.redLightPin, 1)
            GPIO.output(self.greenLightPin, 0)
            GPIO.output(self.blueLightPin, 0)
        elif color == 'G':
            GPIO.output(self.redLightPin, 0)
            GPIO.output(self.greenLightPin, 1)
            GPIO.output(self.blueLightPin, 0)
        elif color == 'B':
            GPIO.output(self.redLightPin, 0)
            GPIO.output(self.greenLightPin, 0)
            GPIO.output(self.blueLightPin, 1)
        elif color == 'W':
            GPIO.output(self.redLightPin, 1)
            GPIO.output(self.greenLightPin, 1)
            GPIO.output(self.blueLightPin, 1)
        elif color == 'R+G':
            GPIO.output(self.redLightPin, 1)
            GPIO.output(self.greenLightPin, 1)
            GPIO.output(self.blueLightPin, 0)
        elif color == 'G+B':
            GPIO.output(self.redLightPin, 0)
            GPIO.output(self.greenLightPin, 1)
            GPIO.output(self.blueLightPin, 1)
        elif color == 'R+B':
            GPIO.output(self.redLightPin, 1)
            GPIO.output(self.greenLightPin, 0)
            GPIO.output(self.blueLightPin, 1)
        elif color == 'OFF':
            GPIO.output(self.redLightPin, 0)
            GPIO.output(self.greenLightPin, 0)
            GPIO.output(self.blueLightPin, 0)
        
    def blinkDevice(self):
        for i in range(0,3):
            self.turnLEDON('W') #White
            t.sleep(.5)
            self.turnLEDON('OFF') #OFF
            t.sleep(.5)
        self.turnLEDON('OFF') #OFF
            
    def turnOnBuzzer(self, access):
        GPIO.output(self.buzzerPin, 1)
        if access == 1:
            t.sleep(.4)
        else:
            t.sleep(.1)
            GPIO.output(self.buzzerPin, 0)
            t.sleep(.1)
            GPIO.output(self.buzzerPin, 1)
            t.sleep(.1)
        GPIO.output(self.buzzerPin, 0)
        
    def doorStatus(self, status):
        if status == 1:
            GPIO.output(self.doorLockPin, status)
        else:
            GPIO.output(self.doorLockPin, status)
    
    def accessDenied(self):
        self.turnLEDON('R') #RED
        self.turnOnBuzzer(0)
        
    def accessGranted(self):
        self.doorStatus(1)
        self.turnLEDON('G') #GREEN
        self.turnOnBuzzer(1)
        
    def enrollmentLEDIndicator(self, color):
        self.turnLEDON('OFF')
        if color == 'R':
            self.turnLEDON('R')
            self.turnOnBuzzer(0)
        elif color == 'G':
            self.turnLEDON('G')
            self.turnOnBuzzer(1)