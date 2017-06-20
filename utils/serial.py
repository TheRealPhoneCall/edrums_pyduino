import serial
from settings import settings

class Serial(object):
    def __init__(self, com_port=settings.COM_PORT, serial_rate=settings.SERIAL_RATE)
        try:
            self.serial = serial.Serial(com_port, serial_rate)
        except Exeption as e:
            self.serial = serial.Serial(serial_rate, serial_rate)
        print "Starting serial communication."
        print self.serial   

    def read_msg(self):        
        serial_msg = self.serial.readline()
        serial_msg = self.serial_msg.split(".")
        return serial_msg

    def parse_msg(self, serial_msg):
        parsed_msg = {
            'cmd': 'note_on' if (serial_msg[0] == 1) else 'note_off',
            'pad': int(serial_msg[1]),
            'velocity': int(serial_msg[2])
        }
        return parsed_msg

    def quit(self):
        print "Serial reading is now terminated."

    class Meta(object):
		verbose_name = _('Serial')
		verbose_name_plural = _('Serial Objects')

	def __str__(self):
		return "{}".format(self.serial)


    