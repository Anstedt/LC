#!/usr/bin/python

# sudo LCgpiotest.py

import RPi.GPIO as GPIO
import time

print "RPi.GPIO Version = ", GPIO.VERSION 

# Use normal GPIO names noy pin names
GPIO.setmode(GPIO.BCM)

# Loop forever looking at gpio
# We will cover all real lanes plus one unused
# NOTE 25 is NOT used, on;y kere for testing
for i in (22, 17, 24, 23, 25):
    print 'GPIO.setup({0:d}, GPIO.IN)'.format(i)
    GPIO.setup(i, GPIO.IN)

cnt = 0
secs = 1
while True:
    print "---------------------------:", cnt, " Update Rate = ", secs, " Second(s)"
    cnt += 1
    for i in (22, 17, 24, 23, 25):
        print 'GPIO.input({0:d}) = {1:d}'.format(i, GPIO.input(i))
    time.sleep(secs)

