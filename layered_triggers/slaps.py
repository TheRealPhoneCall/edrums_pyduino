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

    def __init__(self):
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
        data_array = np.fromstring(data, dtype=np.int16)
        self.spectral_analyzer.process_data(data_array)

        return (data, paContinue)

class StreamProcessor(object):
    FREQS_BUF_SIZE = 11

    def __init__(self):
        self.spectral_analyser = SpectralAnalyser(
            window_size=WINDOW_SIZE,
            segments_buf=RING_BUFFER_SIZE
        )

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
        # get data_array from frame
        data_array = np.fromstring(data, dtype=np.int16)
        # get fundamental frequency
        freq0 = self.spectral_analyser.process_data(data_array)

        # if fundamental frequency is detected, play a note
        if freq0:
            # Onset detected
            print("Note detected; fundamental frequency: ", freq0)
            midi_note_value = int(hz_to_midi(freq0)[0])
            print("Midi note value: ", midi_note_value)
            note = RTNote(midi_note_value, 100, 0.5)
            self.synth.play_note(note)
        return (data, paContinue)

