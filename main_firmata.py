from pyfirmata import Arduino, util
import threading, time, random

import time
from mido import Message, MidiFile, MidiTrack

from utils.settings import *
from utils.velocity import *

# initialize pyfirmata
try:
    board = Arduino('/dev/ttyUSB0')
except:
    board = Arduino('COM5')
print "board initialized via the firmata protocol."
print board

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

def serial_send(ser, data):
    ser.write(data.encode())

def serial_recv(ser):
    return ser.readline()

def get_pin_val(msg_recvd):
    msg_recvd = msg_recvd.split(":")
    return int(msg_recvd[1])

def get_msgs_recvd(msgs_recvd):
    return msgs_recvd.split(",")

def fire_note(pin, note, velocity):

    # play note on
    timedelta=time.time() - start_time
    midi_track('note_on', note, velocity, timedelta)
    player.note_on(note, velocity)

    # play note off
    timedelta=timedelta + TIME_DIFF
    midi_track('note_off', note, velocity, timedelta)
    player.note_off(note, velocity)

def midi_track(cmd, note, velocity, timedelta):    
    track.append(Message(cmd, note=note, velocity=velocity, time=timedelta))

def main():
    try:
        vel_obj = [None for pin in PINS]
        timer = [0 for pin in PINS]
        is_reading = [False for pin in PINS]
        max_velocity = [0 for pin in PINS]

        while True:
            for pin in PINS:
                # initialize vel object
                piezo_val = board.get_pin('a:' + str(pin) + ':i')
                piezo_val = piezo_val.read()
                
                if (piezo_val >= threshold[pin] and not is_reading[pin]):
                    current_time = time.time()
                    if (current_time - timer[pin] >= DEBOUNCE)

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        print "Serial reading is now terminated."

        # save midi msg
        midi.save('from_arduino.mid')
        print "Current MIDI message:"
        print midi_msgs

        # delete player object
        del player
        pygame.midi.quit()


if __name__ == '__main__':
    main()