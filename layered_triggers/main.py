"""
    Sample Runs:
        python main.py -t layered_triggers -cp COM6 -br 31250 -pc basic.json
        python layered_triggers\main.py -cp COM6 -br 31250 -pc basic.json
"""

import sys
import time
import json

# from settings.settings import pads, pad_map
# from utils.velocity import *
# from utils.serial import Serial

from .midos import Midi
from .serials import Serial
from .audiostream import SpectralAnalyser
from settings import *

import numpy as np
from pyaudio import PyAudio, paContinue, paInt16

class StreamProcessor(object):

    FREQS_BUF_SIZE = 11

    def __init__(self, midi_obj, serial_obj, slap_freqs, freq_config):
        # initiate spectral analyzer, midi and serial objects
        self.spectral_analyser = SpectralAnalyser(
            window_size=WINDOW_SIZE,
            segments_buf=RING_BUFFER_SIZE)
        self.midi = midi_obj
        self.serial = serial_obj

        # initiate slap_freq_map variables
        self.current_map = 0
        self.slap_freq_maps = slap_freqs(freq_config)
        self.slap_freq_map = self.slap_freq_maps[self.current_map]    

    def run(self):
        pya = PyAudio()
        self.stream = pya.open(
            format=paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=WINDOW_SIZE,
            stream_callback=self.process_frame,
        )
        self.stream.start_stream()

        while self.stream.is_active() and not raw_input():
            time.sleep(0.1)

        self.stream.stop_stream()
        self.stream.close()
        pya.terminate()

    def process_frame(self, data, frame_count, time_info, status_flag):
        # listen to serial first
        # self.listen_to_serial()

        # then listen to the data frame
        data_array = np.fromstring(data, dtype=np.int16)
        processed_data = self.spectral_analyser.process_data(data_array)
            
        if processed_data:
            freq0 = processed_data['freq0']
            onset = processed_data['onset']    
            dominant_freq = processed_data['dominant_freq']   
            if freq0:
                # slap is detected
                print "Slap detected: \tfund_freq=%s,\t dominant_freq=%s,\t onset=%s" %(freq0, dominant_freq, onset)            

                # loop through the slap_freqs (boom, slap, heck_stick)
                for key in self.slap_freq_map.keys():
                    # set slap_freq to be the value
                    slap_freq = self.slap_freq_map[key]

                    # only fire midi_send when freq0 is within the slap_freq
                    # min_freq and max_freq
                    # if ((freq0 > slap_freq["min_freq"]) and 
                    #     (freq0 < slap_freq["max_freq"])):
                    #     notes = slap_freq["notes"]
                    #     for note in notes:
                    #         self.send_midi_msg("note_on", note)
                    #         self.send_midi_msg("note_off", note)
                    if slap_freq["name"] == "boom":
                        if dominant_freq == "low_dominant":
                            notes = slap_freq["notes"]
                            for note in notes:
                                self.send_midi_msg("note_on", note)
                                self.send_midi_msg("note_off", note)
                    elif slap_freq["name"] == "slap":
                        if dominant_freq == "high_dominant":
                            notes = slap_freq["notes"]
                            for note in notes:
                                self.send_midi_msg("note_on", note)
                                self.send_midi_msg("note_off", note)


        return (data, paContinue)

    def listen_to_serial(self):
        # if a msg is received from nano, reinitiate system
        msg_recvd = self.serial.read_msg()
        print "msg_recvd", msg_recvd

        # if msg is control change, program change, or pitch bend
        if msg_recvd['cmd'] in ['control_change', 'program_change',
                                'pitchwheel']:
            self.send_midi_msg(msg_recvd['cmd'], msg_recvd)

            # for control_change ids 20 and 21, switch the value of 
            # the slap_freq_maps
            if msg_recvd['cmd'] == 'control_change':
                self.control_change(msg_recvd)

    def control_change(self, msg):
        if msg['control'] == 20: # next pad map
            try:
                self.current_map += 1
                self.slap_freq_map = self.slap_freq_maps[self.current_map]
            except:
                self.current_map = 0
                self.slap_freq_map = self.slap_freq_maps[0]
        elif msg['control'] == 21: # prev pad map
            try:
                self.current_map -= 1
                self.slap_freq_map = self.slap_freq_maps[self.current_map]
            except:
                self.current_map = len(self.slap_freq_maps) - 1
                self.slap_freq_map = self.slap_freq_maps[self.current_map]

    def send_midi_msg(self, cmd, msg):
        if cmd in ['note_on', 'note_off']:
            msg = {
                "cmd": cmd, 
                "note": msg['note'],
                "velocity": msg['velocity'],
                "threshold": msg['threshold'], 
                "min_vel": msg['min_vel'],
                "max_vel": msg['max_vel']
            }
        elif cmd in ['control_change', 'program_change', 'pitchwheel']:
            # msg is the same if not note_on/note_off
            msg = msg
            
        midi_msg = self.midi.convert_midi_msg(msg)
        self.midi.store_midi_msg(midi_msg)
        self.midi.send_midi_msg(midi_msg)


def main(com_port, midi_port, baud_rate, freq_config):
    # objects initiation
    serial = Serial(com_port=com_port, serial_rate=baud_rate)
    midi = Midi(virtual_port=midi_port)
    stream = StreamProcessor(midi, serial, slap_freqs, freq_config)
    stream.run()

    # try:
    #     while True:
    #         # if a msg is received from nano, reinitiate system
    #         msg_recvd = serial.read_msg()
    #         print "msg_recvd", msg_recvd

    #         if msg_recvd == {}:
    #             # if no msg, just run the stream               
    #             stream = StreamProcessor(midi, slap_freq_map)
    #             stream.run()

    #         # if msg is control change, program change, or pitch bend
    #         if msg_recvd['cmd'] in ['control_change', 'program_change',
    #                                 'pitchwheel']:
    #             midi_msg = midi.convert_midi_msg(msg_recvd)
    #             midi.store_midi_msg(midi_msg)
    #             midi.send_midi_msg(midi_msg)

    #             # for control_change, switch the value of the slap_freq_maps
    #             if msg_recvd['cmd'] == 'control_change':
    #                 if msg_recvd['control'] == 20: # next pad map
    #                     try:
    #                         current_map += 1
    #                         slap_freq_map = slap_freq_maps[current_map]
    #                     except:
    #                         current_map = 0
    #                         slap_freq_map = slap_freq_maps[0]
    #                 elif msg_recvd['control'] == 21: # prev pad map
    #                     try:
    #                         current_map -= 1
    #                         slap_freq_map = slap_freq_maps[current_map]
    #                     except:
    #                         current_map = len(slap_freq_maps) - 1
    #                         slap_freq_map = slap_freq_maps[current_map]

    #         stream = StreamProcessor(midi, slap_freq_map)
    #         stream.run()
            
    #         # end of block            

    # except KeyboardInterrupt:
    #     print "Keyboard interrupted."
    #     serial.quit()
    #     midi.quit()

if __name__ == "__main__":
    main()