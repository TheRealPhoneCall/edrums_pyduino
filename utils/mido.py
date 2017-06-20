import time
import mido
import serial
# from mido import Message, MidiFile, MidiTrack

import pygame
from pygame.locals import *

# # from settings import settings
from settings import *

class Midi(object):
    def __init__(self, midi_file="utils\midi\output.mid", 
                 virtual_port=MIDI_PORT, instrument=0):
        # instantiate midi
        self.midi_file = midi_file
        self.midi = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.midi.tracks.append(self.track)
        self.track.append(mido.Message('program_change', program=12, time=0))
        self.midi_msgs = []

        # ports
        self.virtual_port = virtual_port
        self.outport = mido.open_output(self.virtual_port)

        # initialize time
        self.start_time = time.time()
        self.prev_time = self.start_time

        # initialize pygame
        pygame.midi.init()
        self.player = pygame.midi.Output(0)
        self.player.set_instrument(instrument)

    def convert_midi_msg(self, msg_json):
        timedelta=time.time() - self.start_time
        midi_msg = mido.Message(msg_json['cmd'], msg_json['note'], 
                                msg_json['velocity'], timedelta) 
        return midi_msg

    def store_midi_msg(self, midi_msg):
        # store note on midi track
        self.midi.tracks.append(midi_msg)
        return midi_msg

    def send_midi_msg(self, midi_msg, port):
        if port == self.virtual_port:
            self.outport.send(midi_msg)
        else:
            # if not equal to default port, re instantiate outport.
            outport = mido.open_output(port)
            outport.send(midi_msg)

    def play_note(self, cmd, note, velocity):
        if cmd == 'note_on':
            player.note_on(note, velocity)
        elif cmd == 'note_off':
            player.note_off(note, velocity)                

    def quit(self):
        self.midi.save(self.midi_file)
        print "Current MIDI message:"
        print self.midi_msgs

        # close port
        self.outport.close()

        # delete player object
        del self.player
        pygame.midi.quit()

class Serial(object):
    def __init__(self, com_port=COM_PORT, serial_rate=SERIAL_RATE):
        try:
            print com_port, serial_rate
            self.serial = serial.Serial(com_port, serial_rate)
        except Exception as e:
            self.serial = serial.Serial(com_port, serial_rate)
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

    def __str__(self):
		return "{}".format(self.serial)
