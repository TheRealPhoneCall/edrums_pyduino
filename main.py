import serial
import time
import pygame.midi
from mido import Message, MidiFile, MidiTrack

from utils.settings import *
from utils.velocity import *

# initialize serial comms
try:
    ser = serial.Serial('/dev/ttyUSB0', 31250)
except:
    ser = serial.Serial('COM5', 31250)
print "Starting serial communication."
print ser

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

    time.sleep(time_diff)

    # play note off
    timedelta=timedelta + TIME_DIFF
    midi_track('note_on', note, velocity, timedelta)
    player.note_off(note, velocity)

def midi_track(cmd, note, velocity, timedelta):    
    track.append(Message(cmd, note, velocity, timedelta))

def main():
    try:
        while True:
            vel_obj = []
            # read serial first
            msgs_recvd = serial_recv(ser)
            msgs_recvd = get_msgs_recvd(msgs_recvd)
            print msgs_recvd

            for pin in PINS:
                # initialize vel object
                msg_recvd = msgs_recvd[pin]
                val = get_pin_val(msg_recvd)
                vel_obj[pin] = Velocity(pin, val)
                
                # keep reading until the peak is reached
                max_peak_is_reached = False
                while not max_peak_is_reached:
                    val = get_pin_val(msg_recvd) 
                    
                    if vel_obj[pin].is_triggered(val): 
                        # if above threshold, find the peak
                        if vel_obj[pin].is_peak_reached():
                            # vel_obj[pin].update_values(val) 

                            # if the peak is reached, check whether this peak
                            # is the max peak of the sensor
                            if vel_obj[pin].is_max_peak_reached(val):
                                # if it is, the note is fired, with the 
                                # velocity calculated from the loop
                                max_peak_is_reached = True
                                note = NOTES[pin]
                                velocity = vel_obj[pin].velocity()
                                fire_note(pin, note, velocity)
                                break
                            else:
                                max_peak_is_reached = False
                    else:
                        # else velocity is zero
                        max_peak_is_reached = False
                    
                    # delay for next reading
                    time.sleep(TIME_DIFF)
                    msg_recvd = serial_recv(ser)
                    print msg_recvd

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