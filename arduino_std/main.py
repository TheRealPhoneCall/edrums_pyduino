import time
import json

# from settings.settings import pads, pad_map
# from utils.velocity import *
# from utils.serial import Serial
from utils.mido import Midi, Serial
from settings import *

def main(com_port, midi_port, pad_config):
    serial = Serial(com_port=com_port)
    midi = Midi(virtual_port=midi_port)
    pads = pads(pad_config)
    try:
        while True:
            # read serial first
            msg_recvd = serial.read_msg()
            print "msg_recvd", msg_recvd
            msg_parsed = serial.parse_msg(msg_recvd)
            print "msg_parsed", msg_parsed

            # get the note from pad_map function
            pads = pads(pad_config)
            note = pad_map(msg_parsed['pad'], pads)
            midi_json = {
                'cmd': msg_parsed['cmd'],
                'note': note,
                'velocity': msg_parsed['velocity']
            }
            print "midi_json", midi_json

            # convert to mido msg
            midi_msg = midi.convert_midi_msg(midi_json)
            print "midi_msg", midi_msg

            # store midi msg then send to virtual port
            midi.store_midi_msg(midi_msg)
            midi.send_midi_msg(midi_msg)

            # end of block            

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        serial.quit()
        midi.quit()