"""
    Sample Runs:
        python main.py -t arduino_std -cp COM6 -br 38400 -pc basic.json
        python arduino_std\main.py -cp COM6 -br 38400 -pc basic.json
"""

import sys
import time
import json

# from settings.settings import pads, pad_map
# from utils.velocity import *
# from utils.serial import Serial

from .midos import Midi
from .serials import Serial
from settings import pads, pad_map

def main(com_port, midi_port, baud_rate, pad_config):
    serial = Serial(com_port=com_port, serial_rate=baud_rate)
    midi = Midi(virtual_port=midi_port)
    pads_config = pads(pad_config)
    try:
        while True:
            # read serial first
            msg_recvd = serial.read_msg()
            print "msg_recvd", msg_recvd

            # get the note from pad_map function
            pad = pads_config["pad" + str(msg_recvd['pad'])]
            notes = pad["notes"]

            # loop through the notes assigned on the pad
            for note in notes: 
                midi_json = {
                    'cmd': msg_recvd['cmd'],
                    'note': note['note'],
                    'velocity': msg_recvd['velocity'],
                    'min_vel': note['min_vel'],
                    'max_vel': note['max_vel'],
                    'threshold': note['threshold']
                }

                # convert to mido msg
                midi_msg = midi.convert_midi_msg(midi_json)
                
                # store midi msg then send to virtual port
                midi.store_midi_msg(midi_msg)
                midi.send_midi_msg(midi_msg)

                # end of block            

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        serial.quit()
        midi.quit()

if __name__ == "__main__":
    sys.path.append("../")

    from main import args
    args = args()

    main(args.com_port, args.midi_port, args.baud_rate, args.pad_config)