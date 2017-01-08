#!/usr/bin/python

# LCgpioraw.py

# Only ouputs lane/time/error data on stdout
# For us we need not worry about blocking
# Logging is used for system errors

# README
# Either the following is output on a call to read_gpio()
#   "000 12345", "001 12345", etc
#   "-01 00000", ONLY ONCE, means no data
#   "-02 eeeee", ONLY ONCE, means some error

import RPi.GPIO as GPIO
import sys
import time
import os

from LClogger import *

# Must be root to do this
os.nice(-20)

class LCgpioraw:
    def __init__(self):
        log.info("LCgpioraw::__init__()")
        log.info("RPi.GPIO Version = %s", GPIO.VERSION)

        log.warn("LCgpioraw::__init__() fix nice() priority also gpio rate")

        # NOTE THIS COULD BE WRONG SINCE I DON'T have IC in front of me
        # L1/CAP-1   L2/CAP-2     Connector
        # GPIO-22    GPIO-17      GPIO-22    GPIO-17

        # L3/CAP-3   L4/CAP-4     Connector
        # GPIO-24    GPIO-23      GPIO-24    GPIO-23

        # Always use seconds
        self.times = [0,   0,  0,  0]
        self.gpios = (22, 17, 24,  23)

        # GPIO_Lane1 = GPIO22
        # GPIO_Lane2 = GPIO17
        # GPIO_Lane3 = GPIO24
        # GPIO_Lane4 = GPIO23
        self.lanes = [False, False, False, False]

        # Yes we should keep running until LCgpio closes our pipe
        self.pipe_open = True

        # Use our board numbers
        GPIO.setmode(GPIO.BCM)

        # Loop through all gpio lanes
        for i in self.gpios:
            log.info("self.gpios=%d", i)
            GPIO.setup(i, GPIO.IN)

    # Read gpio and output strings in these formats
    #   "lll mmmmm", lane/status milliseconds/errors
    #   "001 12345", lane one has taken 12345 milliseconds since last lap
    #   "-01 00000", no lanes have new lap times
    #   "-02 eeeee", some major failure with error code eeeee
    def read_gpio(self):
        lane_time = "-01 00000"
        no_data = True
        for lane_nm in (0,1,2,3):
            # lane_flg is 0 when the car is on the lap counter
            lane_flg = GPIO.input(self.gpios[lane_nm])

            # The car is or was on the lap counter
            if (lane_flg == 0):
                # False here indicates it is a new lap
                if (self.lanes[lane_nm] == False):
                    # But now remember we already counted the car once
                    self.lanes[lane_nm] = True
                    
                    # So if the lane already has some time from the past
                    # we can now determine a new lap time
                    if (self.times[lane_nm] != 0):
                        # So the lane did already have a time so we need the elapsed
                        # time. We are still in floating point seconds here
                        elapsed_time = time.time() - self.times[lane_nm]

                        # Covers cases where times are out of range
                        if (elapsed_time >= 100):
                            elapsed_time = 99.999

                        # Now convert to string in milliseconds
                        elapsed_str = self.secs_to_ms_str(elapsed_time)
                    else:
                        # Default to 99999 milliseconds
                        elapsed_str = "99999"

                    # creates a string of the form "lll ttttt"
                    lane_time = '{0:03d} {1:5s}'.format(lane_nm, elapsed_str)

                    # This is the actual data
                    self.print_stdout(lane_time)

                    # Flush and detect if pipe is closed
                    self.flush_stdout()

                    # There was some data
                    no_data = False

                    # After all of this still need to update new current
                    # time so we can time the next lap
                    self.times[lane_nm] = time.time()
            else:
                # The car is no longer on the lap counter so clear the flag for the next lap
                self.lanes[lane_nm] = False

        # Only flush, don't waste resourcses indciating no cars on lap counter
        if (no_data == True):
            # Set pipe status flags
            self.flush_stdout()

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
    
# Now create the raw gpio
gpioraw = LCgpioraw()

# The time delay in seconds between runs
rate_secs = 0.001

# Run forever
while gpioraw.runit():
    gpioraw.read_gpio()
    time.sleep(rate_secs)
