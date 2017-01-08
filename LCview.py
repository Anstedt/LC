from LClane import *
import time

from LClogger import *

class LCview:
    def __init__(self, vbase, kill_gpio):
        log.info("LCview::__init__()")

        # remember our base graphics
        self.vbase = vbase

        # This is the kill command for LCgpioraw
        self.kill_gpio = kill_gpio

        # log the width and height of the monitor
        log.debug("Width=%d Height=%d", vbase.winfo_screenwidth(), vbase.winfo_screenheight())

        # This creates a full screen window but you need a close button or else you cannot stop the program
        self.vbase.attributes('-fullscreen', True)

        # now create the canvas to draw on
        self.canvas = Canvas(self.vbase, width=self.vbase.winfo_screenwidth(), height=self.vbase.winfo_screenheight(), background = "black")
        # self.canvas = Canvas(self.vbase, width=640, height=480, background = "black")
        
        self.canvas.pack(fill=BOTH)

        # Add Description
        x = 300
        self.canvas.create_text(x, 100, anchor = CENTER, text = "laps", fill = "white", font = ("Helvectica", "70"))
        self.canvas.create_text(x + 370, 100, anchor = CENTER, text = "last", fill = "white", font = ("Helvectica", "70"))
        self.canvas.create_text(x + 720, 100, anchor = CENTER, text = "best", fill = "white", font = ("Helvectica", "70"))

        # How long does it take to create 4 lanes
        beg =  time.clock()

        # now all our lanes        
        self.lanes =   [Lane(self.canvas, 150, 225, "red", 1), \
                        Lane(self.canvas, 150, 350, "green", 2), \
                        Lane(self.canvas, 150, 475, "blue", 3), \
                        Lane(self.canvas, 150, 575, "yellow", 4)]

        # How long did that take
        end =  time.clock()
        log.debug("Lane Time=%s milliseconds", "{0:.3f}".format((end - beg) * 1000))
        
        # Setup escape to end the program
        self.canvas.bind_all("<Escape>", self.killit)

    # lanes start at 0
    def update_lane(self, lane_num, time):
        if (lane_num < len(self.lanes)):
            self.lanes[lane_num].update(time)
        else:
            self.log.warn("Lane numbers go from 0 to %d but we got %d", len(self.lanes)-1, lane_num)

    # End the Lap counter
    def killit(self, event):
        # This tells LCgpio to close the pipe which causes LCgpioraw
        # to see the pipe is closed and shut it self down.
        self.kill_gpio()

        # Now kill off tkinter and all our components
        self.vbase.destroy()
