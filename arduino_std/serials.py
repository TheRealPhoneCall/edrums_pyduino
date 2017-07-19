import serial as ser
from settings import *

class Serial(object):
    def __init__(self, com_port=COM_PORT, serial_rate=SERIAL_RATE):
        try:
            print com_port, serial_rate
            self.serial = ser.Serial(com_port, serial_rate)
        except Exception as e:
            self.serial = ser.Serial(com_port, serial_rate)
        print "Starting serial communication."
        print self.serial   

    def read_msg(self):        
        byte1 = self.serial.readline()
        byte2 = self.serial.readline()
        byte3 = self.serial.readline()
        if byte1 == 0: # note_off command
            serial_msg = {
                'cmd': 'note_off',
                'pad': int(byte2),
                'velocity': int(byte3)
            }
        elif byte1 == 1: # note_on command
            serial_msg = {
                'cmd': 'note_on',
                'pad': int(byte2),
                'velocity': int(byte3)
            }
        elif byte1 == 2: # control change command
            pass
        elif byte1 == 3: # pitch bend command
            serial_msg = {
                'cmd': 'pitchwheel',
                'pitch': int(byte2) if (byte2) else int(byte3),
            }
        else:
            pass
        return serial_msg

    def json_msg(self, serial_msg):
        

    def quit(self):
        print "Serial reading is now terminated."

    def __str__(self):
		return "{}".format(self.serial)