import os, sys, time, fcntl
import multiprocessing
from subprocess import Popen, PIPE

from LClogger import *

class LCgpio:
    def __init__(self):
        log.info("LCgpio::__init__()")

        # Create the gpio process
        # always returns strings via stdout=PIPE of the form:
        # "001 12345", lane one has taken 12345 milliseconds since last lap
        # "-01 00000", no lanes have new lap times
        # "-02 eeeee", some major failure with error code eeeee
        self.myproc = Popen("/srv/public/LC/LCgpioraw.py", bufsize=0, stdout=PIPE, shell=False)

        # Grab only stdout to get the data
        self.pipe_stdout = self.myproc.stdout

        # Create a gpio string list
        self.gpio_str_list = []

        # This changes our pipe to be non-blocking
        fd_stdout = self.pipe_stdout.fileno()
        fl_stdout = fcntl.fcntl(fd_stdout, fcntl.F_GETFL)
        fcntl.fcntl(fd_stdout, fcntl.F_SETFL, fl_stdout | os.O_NONBLOCK)

    # This returns strings, NOT tuples
    def read_gpio(self):
        # If we have no laps/times we need to read more
        if (len(self.gpio_str_list) <= 0):
            # Now we run as long as the pipe exists. Now do a read, the exception
            # is when there is no data, oddly the normal try is valid when the pipe
            # is closed but returns nothing at all instead.
            try:
                # using read so we get multi-lines
                str_buffer = self.pipe_stdout.read()

                # Now break into lists, in our case each list element
                # is a line so this works well
                self.gpio_str_list = str_buffer.split("\n")

                try:
                    self.gpio_str_list.remove('')
                except:
                    log.debug("In this odd case str_buffer did not have a '' at the end")

                # Now grab the first line from the list
                gpio_str = self.gpio_str_list[0]

                # And then pop it from the real list since we used it up
                self.gpio_str_list.pop(0)

            # This is for the case where self.pipe_stdout has no data
            except:
                # If no data to read, then flags as our standard no data message
                gpio_str = "-01 00000"
        else:
            # We don't need a new read since we have already buffered a number of lines

            # Now grab the first line from the list
            gpio_str = self.gpio_str_list[0]

            # And then pop it from the real list since we used it up
            self.gpio_str_list.pop(0)
                
        # If the pipe returns nothing at all it is closed.
        if gpio_str == "":
            # Process is gone or something is wrong, use our -02 error to flag this
            # which normally only happens if process dies or quits for some reason
            gpio_str = "-02 00000"
            log.error("read_gpio PIPE from LCgpioraw must be closed")

        # Notice this is a string at this point
        return gpio_str

    # This function returns tuples
    def read_lanetime(self):
        # return tuple:
        # (001, 12.345), lane one has taken 12.345 seconds since last lap
        # (001, 99.999), lane one has taken more than 99.999 seconds since last lap
        # (-01, 00.000), no lanes have new lap times
        # (-02, ee.eee), some major failure with their error code ee.eee

        # Read the gpio string, assumes it is already cleaned up.
        lanetime = self.read_gpio()

        ################################
        # Now convert string to tuples #
        ################################
        # First break into 2 strings. lane/status amd time in milliseconds
        (lane, time) = lanetime.split(" ")
        
        # Now convert lane to integer for lane or status
        lane = int(lane)

        # now convert time to float in seconds
        time = float(time) / 1000

        # Return the lane/status and time in float for seconds
        return (lane, time)

    # Used to kill LCgpioraw.py by closing the pipe. LCgpioraw can
    # detect this on prints/writes or flushes and works well. But
    # since LCgpioraw writes less often we may just need to kill it
    # instead. see below.
    def kill_gpio(self):
        # This lets LCgpioraw know we are done
        log.info("LCgpio::kill() by closing pipe")
        self.pipe_stdout.close()

        # This kills the process, if you don't catch the exception for the case where the
        # process is already gone then it gets caught on the command line instead.
        try:
            log.info("LCgpio is trying to kill LCgpioraw")
            Popen.kill(self.myproc)
        except:
            log.info("LCgpio has kill LCgpioraw")

        # This returns -9 since that is the signal that killed the process
        log.info("LCgpioraw has been killed via signal %d", self.myproc.poll())
