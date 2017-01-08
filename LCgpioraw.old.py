#!/usr/bin/python

# LCgpioraw.py

# Only ouputs lane/time/error data on stdout
# For us we need not worry about blocking
# Logging is used for system errors

import RPi.GPIO as GPIO
import sys
import time
import os

from LClogger import *

# Debug Only
import random

# Must be root to do this
os.nice(-20)

class LCgpioraw:
    def __init__(self):
        log.info("LCgpioraw::__init__()")
        log.info("RPi.GPIO Version = %s", GPIO.VERSION)

        # NOTE THIS COULD BE WRONG SINCE I DON'T have IC in front of me
        # L1/CAP-1   L2/CAP-2     Connector
        # GPIO-22    GPIO-17      GPIO-22    GPIO-17

        # L3/CAP-3   L4/CAP-4     Connector
        # GPIO-24    GPIO-23      GPIO-24    GPIO-23

        # Always use seconds
        self.def_time = time.time()
        self.times = [0,   0,  0,  0]
        self.gpios = (22, 17, 24,  23)
        self.lanes = [False, False, False, False]
        # Units are seconds with fractions such as 1362424149.49
        self.start_time = time.time()

        # Yes we should keep running until LCgpio closes our pipe
        self.pipe_open = True

        # GPIO_Lane1 = GPIO22
        # GPIO_Lane2 = GPIO17
        # GPIO_Lane3 = GPIO24
        # GPIO_Lane4 = GPIO23

        # Use our board numbers
        GPIO.setmode(GPIO.BCM)

        # Loop through all gpio lanes
        for i in self.gpios:
            log.info("self.gpios=%d", i)
            GPIO.setup(i, GPIO.IN)

##        for io in self.gpios:
##            GPIO.setup(io, GPIO.IN)
##        # GPIO.setup(22, GPIO.IN)
##        # GPIO.setup(17, GPIO.IN)
##        # GPIO.setup(24, GPIO.IN)
##        # GPIO.setup(23, GPIO.IN)

    # LCgpioraw should keep running as long as LCgpio
    # has the pipe open for listening
    def runit(self):
        return(self.pipe_open)

    def flush_stdout(self):
        # Here we can detect if the pipe is closed
        try:
            sys.stdout.flush()
        except:
            # On exception the pipe has been closed by LCgpio
            # This means LCgpioraw should stop since the Lapcounter is gone
            self.pipe_open = False
            log.info("sys.stdout.flush() shows the pipe is closed")                    

    def print_stdout(self, lane_time):
        # Here we can detect if the pipe is closed
        try:
            print lane_time
        except:
            # On exception the pipe has been closed by LCgpio
            # This means LCgpioraw should stop since the Lapcounter is gone
            self.pipe_open = False
            log.info("print_stdout shows the pipe is closed")                    

    # Convert to milliseconds, input is 123.2344444 seconds
    # Example: seconds 12.789
    #          string  "12789"
    def secs_to_ms_str(self, secs):
        # Return should be "00012", "12222", "99999"
        ret = '{0:05d}'.format(int(secs * 1000))
        return(ret)

    # Print strings "lll mmmmm", lane/status milliseconds/errors
    def read_gpio(self):
        lane_time = "-01 00000"
        no_data = True
        for i in (0,1,2,3):
            # Test with no real GPIO
            # lane = random.randrange(0, 2, 1)
            # log.info("CHANGE TO REAL GPIO LCgpioraw:read_gpio() lane=%d", lane)
            
            # alane is 0 when the car is on the lap counter
            alane = GPIO.input(self.gpios[i])

            # if the car is off the lap counter reset it for the next time
            if (alane == 1):
                self.lanes[i] = False

            # In our case 0 means a car is on the lap counter and
            # lanes[i] being false indicates this is the first time
            if (alane == 0 and self.lanes[i] == False):
                # print "DEBUG alane=", alane, " self.lanes[i]=", self.lanes[i], "lanes BEG", self.lanes
                self.lanes[i] = True
                # print "DEBUG lanes END", self.lanes
                # Lane has a time and does have a lap
                if (self.times[i] != 0):
                    # So the lane did already have a time so we need the elapsed
                    # time. We are still in floating point seconds here
                    elapsed_time = time.time() - self.times[i]

                    # Covers cases where times are out of range
                    if (elapsed_time >= 100):
                        elapsed_time = 99.999

                    # Now convert to string in milliseconds
                    elapsed_str = self.secs_to_ms_str(elapsed_time)
                else:
                    # Default to 99999 milliseconds
                    elapsed_str = "99999"

                lane_time = '{0:03d} {1:5s}'.format(i, elapsed_str)
                # prints a string of the form "lll ttttt"

                # This is the actual data
                self.print_stdout(lane_time)

                # Flush and detect if pipe is closed
                self.flush_stdout()

                # There was some data
                no_data = False

                # After all of this still need to update new current time
                self.times[i] = time.time()                

        # Indicate no laps yet
        if (no_data == True):
            self.print_stdout(lane_time)
            # Also sets pipe status flags
            self.flush_stdout()

# Now create the raw gpio
gpioraw = LCgpioraw()

# Run forever
while gpioraw.runit():
    gpioraw.read_gpio()
    # Simulation, act as if cars do 4 second laps
    # self.logger.info("LCgpioraw Still Running")
    time.sleep(0.1)
