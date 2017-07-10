from .midos import Midi
from .serials import Serial
from .slaps import SlapEvent

def main(com_port, midi_port, baud_rate, pad_config):
    serial = Serial(com_port=com_port, serial_rate=baud_rate)
    midi = Midi(virtual_port=midi_port)
    slap = SlapEvent()
    pads_config = pads(pad_config)
    try:
        while True:
            # TODO: Better approach would be to use threading for 
            # different kinds of triggers 
            #------- 1. Read off values from pad first
            # read serial first
            msg_recvd = serial.read_msg()
            print "msg_recvd", msg_recvd

            # get the note from pad_map function
            pad = pad_map(msg_recvd['pad'], pads_config)
            midi_json = {
                'cmd': msg_recvd['cmd'],
                'note': pad['note'],
                'velocity': msg_recvd['velocity']
            }

            # convert to mido msg
            midi_msg = midi.convert_midi_msg(midi_json)
            
            # store midi msg then send to virtual port
            midi.store_midi_msg(midi_msg)
            midi.send_midi_msg(midi_msg)

            #--------2. Listen to slap event
            # detect a slap event
            slap.listen()

            if slap.is_triggered:
                # play the raw slap sound back
                slap.playback()

                # perform spectral analysis
                slap.analyze_spectrum()

                # detect pitch and amp
                freq = slap.detect_pitch()
                amp = slap.detect_amplitude()

                # map freq and amplitude to respective
                # note and velocity components
                note = freq_map(freq)
                vel = amp_map(amp)

                # get msg and clean it for sending/storing
                midi_on_json = {'cmd': 'note_on', 'note': note, 
                                'velocity': vel}
                midi_off_json = {'cmd': 'note_off', 'note': note, 
                                'velocity': vel} 
                midi_on_msg = midi.convert_midi_msg(midi_on_json)
                midi_off_msg = midi.convert_midi_msg(midi_off_json)

                # store and send to virtual port
                midi.store_midi_msg(midi_on_msg)
                midi.store_midi_msg(midi_off_msg)
                midi.send_midi_msg(midi_on_msg)
                midi.send_midi_msg(midi_off_msg)


            # end of block            

    except KeyboardInterrupt:
        print "Keyboard interrupted."
        serial.quit()
        midi.quit()

if __name__ == "__main__":
    main()