'''
    Major Credits to Anna Wszeborowska
'''

import time
import itertools
from collections import deque

import numpy as np
from pyaudio import PyAudio, paContinue, paInt16

from settings import (
    RING_BUFFER_SIZE,
    SAMPLE_RATE,
    THRESHOLD_MULTIPLIER,
    THRESHOLD_WINDOW_SIZE,
    WINDOW_SIZE)


class SpectralAnalyser(object):

    FREQUENCY_RANGE = (500, 1200)

    def __init__(self, window_size, segments_buf=None):
        self.window_size = window_size
        if segments_buf is None:
            segments_buf = int(SAMPLE_RATE / window_size)
        self.segments_buf = segments_buf

        self.thresholding_window_size = THRESHOLD_WINDOW_SIZE
        assert self.thresholding_window_size <= segments_buf

        self.last_spectrum = np.zeros(window_size, dtype=np.int16)
        self.last_flux = deque(
            np.zeros(segments_buf, dtype=np.int16), segments_buf)
        self.last_prunned_flux = 0

        self.hanning_window = np.hanning(window_size)
        # The zeros which will be used to double each segment size
        self.inner_pad = np.zeros(window_size)

        # To ignore the first peak just after starting the application
        self.first_peak = True

    def get_flux_for_thresholding(self):
        return list(itertools.islice(
            self.last_flux,
            self.segments_buf - self.thresholding_window_size,
            self.segments_buf))

    def find_onset(self, spectrum):
        """
        Calculates the difference between the current and last spectrum,
        then applies a thresholding function and checks if a peak occurred.
        """
        last_spectrum = self.last_spectrum
        flux = sum([max(spectrum[n] - last_spectrum[n], 0)
            for n in xrange(self.window_size)])
        self.last_flux.append(flux)

        thresholded = np.mean(
            self.get_flux_for_thresholding()) * THRESHOLD_MULTIPLIER
        prunned = flux - thresholded if thresholded <= flux else 0
        peak = prunned if prunned > self.last_prunned_flux else 0
        self.last_prunned_flux  = prunned
        return peak

    def find_fundamental_freq(self, samples):
        cepstrum = self.cepstrum(samples)
        # search for maximum between 0.08ms (=1200Hz) and 2ms (=500Hz)
        # as it's about the recorder's frequency range of one octave
        min_freq, max_freq = self.FREQUENCY_RANGE
        start = int(SAMPLE_RATE / max_freq)
        end = int(SAMPLE_RATE / min_freq)
        narrowed_cepstrum = cepstrum[start:end]

        peak_ix = narrowed_cepstrum.argmax()
        freq0 = SAMPLE_RATE / (start + peak_ix)

        if freq0 < min_freq or freq0 > max_freq:
            # Ignore the note out of the desired frequency range
            return

        return freq0

    def find_dominant_freq_region(self, spectrum):
        high_freq_number = 90
        spectrum_low_size = 600
        spectrum_high_size = WINDOW_SIZE - spectrum_low_size

        spectrum_low = spectrum[:spectrum_low_size]        
        spectrum_high = spectrum[spectrum_low_size:]

        avg_psd_low = sum(spectrum_low)
        avg_psd_high = sum(spectrum_high)

        num_low_freqs = sum(i > 10 for i in spectrum_low)
        num_high_freqs = sum(i > 10 for i in spectrum_high)
        
        print "spectrum_low_num: ", num_low_freqs
        print "spectrum_high_num:", num_high_freqs
        # print "spectrum_low=%s,\tspectrum_high=%s" %(len(spectrum_low), len(spectrum_high))
        print "avg_psd_low=%s,\tavg_psd_high=%s" %(avg_psd_low, avg_psd_high)
        if num_high_freqs < high_freq_number:
            # detects boom slap
            return "low_dominant"
        else:
            # detects snare slap
            return "high_dominant"

    def process_data(self, data):
        spectrum = self.autopower_spectrum(data)
        onset = self.find_onset(spectrum)
        
        self.last_spectrum = spectrum

        if self.first_peak:
            self.first_peak = False
            return {"freq0": None, "dominant_freq": None, "onset": None}

        if onset:
            # freq0 = self.find_fundamental_freq(data)
            freq0 = 1
            dominant_freq = self.find_dominant_freq_region(spectrum)
            
            # print "spectrum length: ", len(spectrum)
            # for spec in spectrum:
            #     print spec, ", "
            # print "onset: ", onset
            return {"freq0": freq0, "dominant_freq": dominant_freq, "onset": onset}

    def autopower_spectrum(self, samples):
        """
        Calculates a power spectrum of the given data using the Hamming window.
        """
        # TODO: check the length of given samples; treat differently if not
        # equal to the window size

        windowed = samples * self.hanning_window
        # Add 0s to double the length of the data
        padded = np.append(windowed, self.inner_pad)
        # Take the Fourier Transform and scale by the number of samples
        spectrum = np.fft.fft(padded) / self.window_size
        autopower = np.abs(spectrum * np.conj(spectrum))
        return autopower[:self.window_size]

    def cepstrum(self, samples):
        """
        Calculates the complex cepstrum of a real sequence.
        """
        spectrum = np.fft.fft(samples)
        log_spectrum = np.log(np.abs(spectrum))
        cepstrum = np.fft.ifft(log_spectrum).real
        return cepstrum