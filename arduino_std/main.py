"""
    Sample Runs:
        python main.py -t arduino_std -cp COM6 -br 31250 -pc basic.json
        python arduino_std\main.py -cp COM6 -br 31250 -pc basic.json
"""

import sys
import time
import json

# from settings.settings import pads, pad_map
# from utils.velocity import *
# from utils.serial import Serial

from .midos import Midi
from .serials import Serial
from settings import pads

def main(com_port, midi_port, baud_rate, pad_config):
    # object initiations
    serial = Serial(com_port=com_port, serial_rate=baud_rate)
    midi = Midi(virtual_port=midi_port)

    # pad maps initiation
    current_map = 0
    pad_maps = pads(pad_config)
    pad_map = pad_maps[current_map]
    try:
        while True:
            # read serial first
            msg_recvd = serial.read_msg()
            if msg_recvd == {}:
                continue

            # if msg is control change, program change, or pitch bend
            if msg_recvd['cmd'] in ['control_change', 'program_change',
                                    'pitchwheel']:
                midi_msg = midi.convert_midi_msg(msg_recvd)
                midi.store_midi_msg(midi_msg)
                midi.send_midi_msg(midi_msg)

                # for control_change, switch the value of the pad_maps
                if msg_recvd['cmd'] == 'control_change':
                    if msg_recvd['control'] == 20: # next pad map
                        try:
                            current_map += 1
                            pad_map = pad_maps[current_map]
                        except:
                            current_map = 0
                            pad_map = pad_maps[0]
                    elif msg_recvd['control'] == 21: # prev pad map
                        try:
                            current_map -= 1
                            pad_map = pad_maps[current_map]
                        except:
                            current_map = len(pad_maps) - 1
                            pad_map = pad_maps[current_map]
            # else it's a note_on/note_off msg
            else:
                # get the note from pad_map function
                pad = pad_map["pad" + str(msg_recvd['pad'])]
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