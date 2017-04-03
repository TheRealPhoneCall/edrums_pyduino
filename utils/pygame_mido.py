import serial
import pygame.midi
from mido import Message, MidiFile, MidiTrack

import time
from datetime import timedelta as timedelta

# instantiate serial
serial = serial.Serial('/dev/ttyUSB0', 31250)
print "Starting serial communication."
print serial

# instantiate midi
midi = MidiFile()
track = MidiTrack()
midi.tracks.append(track)

# initialize time
start_time = time.time()
prev_time = start_time

# instantiate track:
track.append(Message('program_change', program=12, time=0))
midi_msgs = []

# instantiate pygame player
pygame.midi.init()
player = pygame.midi.Output(0)
GRAND_PIANO = 0
CHURCH_ORGAN = 19
player.set_instrument(0)



try:
    # loop through the midi messages received
    while True:
        # read the midi msg
        midi_read = serial.readline()
        midi_read = midi_read.split(".")
        current_time = time.time()
        midi_msg = {
            'note_cmd': 'note_on' if int(midi_read[0]) == 90 else 'note_off',
            'note': int(midi_read[1]),
            'velocity': int(midi_read[2]),
            'timedelta': int(current_time-start_time)
        }

        # print and append midi msg
        print "reading midi:"
        print midi_msg
        midi_msgs.append(midi_msg)

        # play midi msg
        if midi_msg['note_cmd'] == 'note_on':
            player.note_on(midi_msg['note'], midi_msg['velocity'])
        else:
            player.note_off(midi_msg['note'], midi_msg['velocity'])
        
        # append track
        track.append(Message(midi_msg['note_cmd'], note=midi_msg['note'], 
                             velocity=midi_msg['velocity'], 
                             time=midi_msg['timedelta']))
        
        # store current_time as prev_time
        prev_time = current_time

except KeyboardInterrupt:
    print "Keyboard interrupted."
    print "Serial reading is now terminated."
    midi.save('from_arduino.mid')
    print "Current MIDI message:"
    print midi_msgs

    del player
    pygame.midi.quit()
    