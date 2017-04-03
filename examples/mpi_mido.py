#!/usr/bin/env python2
""" Records midi messages sent by arduino, 
    then broadcasts it to the other pis.
"""
from mpi4py import MPI
from mpi import initialize_msgs, mpi_transmit
from mido import Message, MidiFile, MidiTrack
import time
import serial

# initialize mpi
comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

# initialize serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600)
print "Starting serial communication."
print ser

# initialize midi
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# instantiate track:
start_time = time.time()
prev_time = start_time
track.append(Message('program_change', program=12, time=0))
midi_msgs = initialize_msgs(comm, size)
old_midi_msg = ""

if rank == 0:
    try:
        # loop through the midi messages received
        while True:
            # get the midi msgs
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

            # transmit midi msg
            midi_msgs[rank].append(midi_msg)
            mpi_transmit(comm, rank, size, data=midi_msg, src=0)

            # append to track
            track.append(Message(midi_msg['note_cmd'], note=midi_msg['note'], 
                                 velocity=midi_msg['velocity'], time=midi_msg['timedelta']))
            prev_time = current_time
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."

for rank in range(size):
    if rank is not 0:
        try:
            # receive the midi msg 
            midi_msg = comm.recv(source=0)
            midi_msgs[rank].append(midi_msg)

            # append to track
            track.append(Message(midi_msg['note_cmd'], note=midi_msg['note'], 
                                velocity=midi_msg['velocity'], time=midi_msg['timedelta']))
        except Exception as e:
            print "Error in the child rank."
            print e.msg()

# Save the midi message:
mid.save('from_arduino.mid')
print "Current MIDI message:"
print midi_msgs

