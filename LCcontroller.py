from LCview import *
from LCgpio import *

from LClogger import *

import random

class LCcontroller:
    def __init__(self):
        log.info("LCcontroller::__init__()")

        self.base = Tk()
        self.gpio = LCgpio()

        # The callback self.gpio.kill_gpio, executed when the user
        # hits the escape key, allows LCview to send a message to
        # LCgpio to close the LCgpioraw pipe which in turn shuts-down
        # the LCgpioraw process.

        self.view = LCview(self.base, self.gpio.kill_gpio)
        
        # Use timed callback to request any new lane times
        self.check_lane_updates()

    # At a period of our selection we jump out of tkinter to
    # see if we have new laps or times
    def check_lane_updates(self):
        # Get lane updates
        self.get_lane_updates()

        # After we have our lane updates let tkinter run for
        # a while but check again in 100 milliseconds, 0.1 seconds.
        self.base.after(100, self.check_lane_updates)

    # This function calls the gpio interface to check for new lane/lap times
    def get_lane_updates(self):
        # lane is an integer, -02=error, -01=no updates, 0 through 3, for lanes
        # timeit is float time in seconds, 00.000 though 99.999. Note that
        # 99.999 can also mean no real time, such as first lap or car off track
        # for more than 100 seconds.
        (lane, timeit) = self.gpio.read_lanetime()

        log.debug("lane=%d time=%f", lane, timeit)

        # If lane 0 through 3 we have a new lane time.
        if (lane >= 0):
            self.view.update_lane(lane, timeit)
        elif (lane == -1): # here we just have no new laps
            log.debug("LCcontroller::get_lane_updates() No New Laps")
        else: # -02 or less so we have an unrecoverbale error.
            log.error("LCcontroller::get_lane_updates() pipe frpm gpio must be closed")

    # This is the tkinter main event loop
    def mainloop(self):
        self.base.mainloop()
