#!/usr/bin/python
#
# Read stream of lines from a Arduino Firmata. This
# produces 3 values per line every 50ms that relate to the orientation
# of the sensor. 
#
# This script supports both Python 2.7 and Python 3

from __future__ import print_function, division, absolute_import
import sys
from pyfirmata import Arduino, util

if sys.hexversion > 0x02ffffff:
    import tkinter as tk
else:
    import Tkinter as tk
from serial import Serial

# initialize pyfirmata
try:
    board = Arduino('/dev/ttyUSB0')
except:
    board = Arduino('COM6')
print("board initialized via the firmata protocol.")
print(board)


class App(tk.Frame):
    def __init__(self, parent, title, board):
        tk.Frame.__init__(self, parent)
        self.board = board
        self.npoints = 100
        self.Line1 = [0 for x in range(self.npoints)]
        self.Line2 = [0 for x in range(self.npoints)]
        self.Line3 = [0 for x in range(self.npoints)]
        parent.wm_title(title)
        parent.wm_geometry("800x400")
        self.canvas = tk.Canvas(self, background="white")
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.create_line((0, 0, 0, 0), tag='X', fill='darkblue', width=1)
        self.canvas.create_line((0, 0, 0, 0), tag='Y', fill='darkred', width=1)
        self.canvas.create_line((0, 0, 0, 0), tag='Z', fill='darkgreen', width=1)
        self.canvas.grid(sticky="news")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky="news")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def on_resize(self, event):
        self.replot()

    def read_serial(self):
        """
        Check for input from the serial port. On fetching a line, parse
        the sensor values and append to the stored data and post a replot
        request.
        """
        try:
            x = board.get_pin('a:0:i').read()   # val from pad 0
            y = board.get_pin('a:1:i').read()   # val from pad 1
            z = board.get_pin('a:2:i').read()   # val from pad 2            
            self.append_values(x, y, z)
            self.after_idle(self.replot)
        except Exception as e:
            print(e)
        self.after(10, self.read_serial)

    def append_values(self, x, y, z):
        """
        Update the cached data lists with new sensor values.
        """
        self.Line1.append(float(x))
        self.Line1 = self.Line1[-1 * self.npoints:]
        self.Line2.append(float(y))
        self.Line2 = self.Line2[-1 * self.npoints:]
        self.Line3.append(float(z))
        self.Line3 = self.Line3[-1 * self.npoints:]
        return

    def replot(self):
        """
        Update the canvas graph lines from the cached data lists.
        The lines are scaled to match the canvas size as the window may
        be resized by the user.
        """
        w = self.winfo_width()
        h = self.winfo_height()
        max_X = max(self.Line1) + 1e-5
        max_Y = max(self.Line2) + 1e-5
        max_Z = max(self.Line3) + 1e-5
        max_all = 200.0
        coordsX, coordsY, coordsZ = [], [], []
        for n in range(0, self.npoints):
            x = (w * n) / self.npoints
            coordsX.append(x)
            coordsX.append(h - ((h * (self.Line1[n]+100)) / max_all))
            coordsY.append(x)
            coordsY.append(h - ((h * (self.Line2[n]+100)) / max_all))
            coordsZ.append(x)
            coordsZ.append(h - ((h * (self.Line3[n] + 100)) / max_all))
        self.canvas.coords('X', *coordsX)
        self.canvas.coords('Y', *coordsY)
        self.canvas.coords('Z', *coordsZ)

def main(args = None):
    if args is None:
        args = sys.argv
    port,baudrate = 'COM5', 115200
    if len(args) > 1:
        port = args[1]
    if len(args) > 2:
        baudrate = int(args[2])
    root = tk.Tk()
    app = App(root, "Smooth Sailing", board)
    app.read_serial()
    app.mainloop()
    return 0

if __name__ == '__main__':
    sys.exit(main())