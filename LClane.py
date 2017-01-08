from Tkinter import *

class Lane:

    def __init__(self, vcanvas, x, y, textcolor, lanenum):
        self.canvas = vcanvas
        self.x = x
        self.y = y
        self.textcolor = textcolor
        self.lanenum = lanenum
        self.laps = 0
        self.besttime = 99.999
        self.currenttime = 99.999
        fontwidth = "70"
        justification = NE
        # lanes being printed
        lanetext = "L"+str(lanenum)
        self.lanetext = self.canvas.create_text(x, y, anchor=justification, text=lanetext, fill=textcolor, font=("Helvectica", fontwidth))

        # laps being printed
        lapstext = "{0:3d}".format(self.laps)
        self.lapstext = self.canvas.create_text(x + 230, y, anchor=justification, text=lapstext, fill=textcolor, font=("Helvectica", fontwidth))

        # current time being printed
        if (self.currenttime >= 99.999):
            currenttimetext = "--.---"
        else:
            currenttimetext = "{0:.3f}".format(self.currenttime)
        self.currenttimetext = self.canvas.create_text(x + 610, y, anchor=justification, text=currenttimetext, fill=textcolor, font=("Helvectica", fontwidth))

        # best time being printed
        if (self.besttime >= 99.999):
            besttimetext = "--.---"
        else:
            besttimetext = "{0:.3f}".format(self.besttime)
        self.besttimetext = self.canvas.create_text(x + 980, y, anchor=justification, text=besttimetext, fill=textcolor, font=("Helvectica" ,fontwidth))

    def update(self, time):
        # update the laps
        self.laps += 1
        lapstext = "{0:3d}".format(self.laps)
        self.canvas.itemconfigure(self.lapstext, text=lapstext)

        # update the current time
        self.currenttime = time
        if (self.currenttime >= 99.999):
            currenttimetext = "--.---"
        else:
            currenttimetext = "{0:.3f}".format(self.currenttime)
        self.canvas.itemconfigure(self.currenttimetext, text=currenttimetext)

        # update the best time Jeremy
        # explains how to operate best time
        if (self.besttime == 0):
            self.besttime = time
        elif (time < self.besttime):
            self.besttime = time

        # drawing besttime number
        if (self.besttime >= 99.999):
            besttimetext = "--.---"
        else:
            besttimetext = "{0:.3f}".format(self.besttime)
        self.canvas.itemconfigure(self.besttimetext, text=besttimetext)
