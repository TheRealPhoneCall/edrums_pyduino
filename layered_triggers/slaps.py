import pyaudio
import numpy as np

FORMAT = pyaudio.paInt16
CHANNELS = 1
CHANNEL_IN = 2
CHANNEL_OUT = 5
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
VIRTUAL_MIDI_PORT = "berdrums"

class SlapEvent(object):

    def __init__(self, midi_obj):
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
        self.midi = midi_obj    

    def listen(self):
        # TODO: listens to the instrument to detect any 
        # slap event
        pass    

    def analyze_spectrum(self):
        pass

    def detect_pitch(self):
        start = int(fs/1200)
        end = int(fs/500)
        narrowed_ceptstrum = ceptstrum[start:end]

        peak_index = narrowed_ceptstrum.argmax()
        fundamental_freq = fs/(start+peak_index)

        return fundamental_freq

    def detect_amplitude(self):
        # assume to be half of the max velocity for now
        amp = int(127/2)
        return amp

    def playback(self, volume):
        # TODO: the audio streamed has to be playedback too
        # with the volume set by its control panel
        pass        

    def msg_out(self, freq, amp):
        msg_json = {"freq": note, "amp": amp}
        return msg_json

    def callback(self, data, frame_count, time_info, status_flag):
        data_array = np.fromString(data, dtype=np.int16)
        self.spectral_analyzer.process_data(data_array)

        return (data, paContinue)