import pyaudio
import numpy as np
from mido import Message, MidiFile, MidiTrack

FORMAT = pyaudio.paInt16
CHANNELS = 1
CHANNEL_IN = 2
CHANNEL_OUT = 5
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
VIRTUAL_MIDI_PORT = "berdrums"

class SlapRecord(object):

    def __init__(self, ):
        # instatntiate pyaudio
        pyaudio = pyaudio.PyAudio()
        self.stream = pyaudio.open(
            format=paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=WINDOW_SIZE,
            stream_callback=self.callback,
        )
        self.stream.start_stream()

        # instantiate mido
        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(track)
        self.track.append(Message('program_change', program=12, time=0))

        # instantiate midi virtual port
        self.port = mido.open_output(VIRTUAL_MIDI_PORT)
        

    def spectral_analyzer(self):
        pass

    def detect_pitch(self):
        start = int(fs/1200)
        end = int(fs/500)
        narrowed_ceptstrum = ceptstrum[start:end]

        peak_index = narrowed_ceptstrum.argmax()
        fundamental_freq = fs/(start+peak_index)

        return fundamental_freq

    def playback(self, freq):
        current_time = time.time()
        self.send_to_port(midi_msg=self.midi.Message('note_on', note=freq))
        self.send_to_port(midi_msg=self.midi.Message('note_off', note=freq))

    def send_to_port(self, midi_msg):
        self.port.send(midi_msg)

    def callback(self, data, frame_count, time_info, status_flag):
        data_array = np.fromString(data, dtype=np.int16)
        self.spectral_analyzer.process_data(data_array)

        return (data, paContinue)