from mido import Message, MidiFile, MidiTrack
import time
import datetime
from datetime import timedelta as timedelta

import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)
print "Starting serial communication."
print ser

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

start_time = time.time()
prev_time = start_time

# instantiate track:
track.append(Message('program_change', program=12, time=0))
midi_msgs = []
old_midi_msg = ""

try:
    # loop through the midi messages received
    while True:
        ser.readline()
        midi_msg = ser.readline()
        midi_msg = midi_msg.split(".")
        # print midi_msg
        current_time = time.time()
        midi_msg = {
            'note_cmd': 'note_on' if int(midi_msg[0]) == 90 else 'note_off',
            'note': int(midi_msg[1]),
            'velocity': int(midi_msg[2]),
            'timedelta': int(current_time-prev_time)
        }
        print "reading midi:"
        print midi_msg
        midi_msgs.append(midi_msg)

        old_midi_msg = midi_msg
        prev_time = current_time

        track.append(Message(midi_msg['note_cmd'], note=midi_msg['note'], 
                             velocity=midi_msg['velocity'], time=midi_msg['timedelta']))
except KeyboardInterrupt:
    print "Keyboard interrupted."
    print "Serial reading is now terminated."
    mid.save('from_arduino.mid')
    print "Current MIDI message:"
    print midi_msgs
    