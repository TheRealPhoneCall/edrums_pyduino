import time
import sys
import mido
import pygame
from pygame.locals import *

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
        # self.inport = mido.open_input(self.virtual_port)

        # initialize time
        self.start_time = time.time()
        self.prev_time = self.start_time

        # initialize pygame
        # pygame.midi.init()
        # self.player = pygame.midi.Output(0)
        # self.player.set_instrument(instrument)

    def map_velocity(self, msg_json):
        # maps velocity values based on the min and max vals specified
        if msg_json['velocity'] < msg_json['threshold']:
            return 0
        else:
            return int((msg_json['velocity']-0) * (msg_json['max_vel']-msg_json['min_vel']) / 
                    (127-0) + msg_json['min_vel'])

    def convert_midi_msg(self, msg_json):
        timedelta = time.time() - self.start_time
        if msg_json['cmd'] in ['note_on', 'note_off']:
            velocity = self.map_velocity(msg_json)
            midi_msg = mido.Message(msg_json['cmd'], note=msg_json['note'], 
                                    velocity=velocity, time=timedelta) 
        elif msg_json['cmd'] == 'pitchwheel':
            midi_msg = mido.Message(msg_json['cmd'], pitch=msg_json['pitch'], 
                                    time=timedelta)
        elif msg_json['cmd'] == 'control_change':
            midi_msg = mido.Message(msg_json['cmd'], control=msg_json['control'], 
                                    time=timedelta)
        else:
            midi_msg = mido.Message()
        return midi_msg

    def store_midi_msg(self, midi_msg):
        # store note on midi track
        self.midi.tracks.append(midi_msg)
        return midi_msg

    def send_midi_msg(self, midi_msg, port=MIDI_PORT):
        if port == self.virtual_port:
            self.outport.send(midi_msg)
        else:
            # if not equal to default port, re instantiate outport.
            outport = mido.open_output(port)
            outport.send(midi_msg)
        
        print "sent to '%s': \t %s" %(port, midi_msg)

    def recv_midi_msg(self, midi_msg, port=MIDI_PORT):
        # TODO: Explore MIDI reading from bytes of data
        if port == self.virtual_port:
            msg = self.inport.receive(midi_msg)
        else:
            # if not equal to default port, re instantiate outport.
            inport = mido.open_input(port)
            msg = inport.receive(midi_msg)
        
        print "recvd from '%s': \t %s" %(port, midi_msg)

    # def play_note(self, cmd, note, velocity):
    #     if cmd == 'note_on':
    #         player.note_on(note, velocity)
    #     elif cmd == 'note_off':
    #         player.note_off(note, velocity)                

    def quit(self):
        self.midi.save(self.midi_file)
        # print "Current MIDI message:"
        # print self.midi_msgs

        # close port
        self.outport.close()

        # delete player object
        # del self.player
        # pygame.midi.quit()

