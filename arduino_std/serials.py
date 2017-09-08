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
        byte1 = int(byte1)
        byte2 = int(byte2)
        byte3 = int(byte3)

        # print byte1, byte2, byte3
        
        if byte1 == 0: # note_off command
            serial_msg = {
                'cmd': 'note_off',
                'pad': byte2,
                'velocity': byte3
            }
            # print byte2
        elif byte1 == 1: # note_on command
            serial_msg = {
                'cmd': 'note_on',
                'pad': byte2,
                'velocity': byte3
            }
            # print byte2
        elif byte1 == 2: # control change command
            serial_msg = {
                'cmd': 'control_change',
                'control': byte2,
                'value': byte3 
            }
        elif byte1 == 3: # pitch bend command
            serial_msg = {
                'cmd': 'pitchwheel',
                'pitch': byte2 if (byte2) else byte3,
            }
        else:
            serial_msg = {}
        return serial_msg

    def quit(self):
        print "Serial reading is now terminated."

    def __str__(self):
        return "{}".format(self.serial)