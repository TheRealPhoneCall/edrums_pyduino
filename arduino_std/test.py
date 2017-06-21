import sys
import time
import json

import mido
import pygame
from pygame.locals import *

MIDI_PORT = u"berdrums 1"

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

        with open("midi_files\sample_midi.json") as midi_file:
            midi_file = json.load(midi_file)            
            self.notes = midi_file['midi']

        # ports
        self.virtual_port = virtual_port
        self.outport = mido.open_output(self.virtual_port)

        # initialize time
        self.start_time = time.time()
        self.prev_time = self.start_time

    def convert_midi_msg(self, msg_json):
        timedelta=time.time() - self.start_time
        midi_msg = mido.Message(msg_json['cmd'], note=msg_json['note'], 
                                velocity=msg_json['velocity'], time=timedelta) 
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
        
        print "sent to vitual port: " + port
        print "midi msg: ", midi_msg

    def recv_midi_msg(self, midi_msg, port=MIDI_PORT):
        # TODO: Explore MIDI reading from bytes of data
        if port == self.virtual_port:
            msg = self.inport.receive(midi_msg)
        else:
            # if not equal to default port, re instantiate outport.
            inport = mido.open_input(port)
            msg = inport.receive(midi_msg)
        
        print "recvd from vitual port: " + port
        print "midi msg: ", midi_msg

    def loop_through_midi_json(self):
        for i in xrange(len(self.notes)):
            midi_json = self.notes[i]
            print midi_json
            midi_msg = self.convert_midi_msg(midi_json)
            midi_msg = self.store_midi_msg(midi_msg)
            self.send_midi_msg(midi_msg)
            
            if (i % 2):
                time.sleep(1)                         

    def quit(self):
        self.midi.save(self.midi_file)
        print "Current MIDI message:"
        print self.midi_msgs

        # close port
        self.outport.close()

        # delete player object
        # del self.player
        # pygame.midi.quit()


def main(midi_port="berdrums 1"):
    midi = Midi()
    try:
        while True:
            # just loop through all notes on json file
            midi.loop_through_midi_json()
            # end of block            

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        serial.quit()
        midi.quit()

if __name__ == "__main__":
    main()