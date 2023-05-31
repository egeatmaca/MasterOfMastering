import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import pydub
import pydub.effects
import os
import config

ZERO_DIVISION_ADJUSTMENT = 10**-10

class MasterOfMastering:
    DEFAULT_STEPS = config.DEFAULT_STEPS
    DEFAULT_SETTINGS = config.DEFAULT_SETTINGS
    PROFILES = config.PROFILES


    def __init__(self, input_path, output_path, steps=DEFAULT_STEPS, settings=DEFAULT_SETTINGS, profile='default'):
        self.input_path = input_path
        self.output_path = output_path
        self.steps = steps
        self.settings = settings
        self.profile = MasterOfMastering.PROFILES[profile]

        # Fill in missing settings with default settings
        for step in steps:
            if step not in settings.keys() and step in self.DEFAULT_SETTINGS.keys():
                settings[step] = self.DEFAULT_SETTINGS[step]


    def calculate_equalization_settings(self):
        # Get equalization profile
        eq_profile = self.profile['equalization']

        # Get target band energies from profile
        target_band_energies = eq_profile['target_band_energies']

        # Load audio file
        sample_rate, audio = wav.read(self.input_path)

        # Apply FFT to audio to obtain frequency spectrum
        frequency_bins, segment_spectrum = signal.periodogram(audio, fs=sample_rate, window='hamming')
        
        # Initialize gain_adjustments
        gain_adjustments = {}

        # For each frequency band and target energy in profile
        for band, target_energy in target_band_energies.items():
            # Calculate energy in each frequency band for each segment
            energy = np.sum(segment_spectrum[:, (frequency_bins >= band) &
                                                 (frequency_bins < band * 10)],
                                axis=1)
            
            # Calculate mean energy in each frequency band
            mean_energy = np.mean(energy)

            # Calculate gain adjustment
            gain_adjustment = (target_energy - mean_energy) / (mean_energy + ZERO_DIVISION_ADJUSTMENT)

            # Set equalization settings for band
            gain_adjustments[band] = gain_adjustment

        # Limit gain adjustments between -1 and 1
        for band, gain in gain_adjustments.items():
            if gain < -1:
                gain_adjustments[band] = -1
            elif gain > 1:
                gain_adjustments[band] = 1

        # Set and return equalization settings
        eq_settings = {'gain_adjustments': gain_adjustments}
        self.settings['equalization'] = eq_settings
        return eq_settings
    

    def calculate_compression_settings(self):
        # TODO: Implement compression settings calculation
        return self.DEFAULT_SETTINGS['compression']


    def clear_output(self):
        if os.path.exists(self.output_path):
            os.system('rm ' + self.output_path)


    def apply_normalization(self, headroom=0.1):
        # Load and normalize audio file with pydub
        audio = pydub.AudioSegment.from_file(self.input_path)
        normalized_audio = pydub.effects.normalize(audio, headroom=headroom)
        self.clear_output()
        normalized_audio.export(self.output_path, format="wav")


    def apply_equalization(self, gain_adjustments):
        # Load audio file
        audio = pydub.AudioSegment.from_file(self.input_path)

        # Apply equalization settings to audio
        equalized_audio = None
        for band, gain_adjustment in gain_adjustments.items():
            band_audio = pydub.effects.low_pass_filter(audio, band)
            band_audio = pydub.effects.high_pass_filter(band_audio, band * 10)
            band_audio = pydub.effects.pan(band_audio, gain_adjustment)
            
            if equalized_audio is None:
                equalized_audio = band_audio
            else:
                equalized_audio = equalized_audio.overlay(band_audio)

        # Export equalized audio to output file
        self.clear_output()
        equalized_audio.export(self.output_path, format="wav")


    def apply_compression(self, threshold, ratio):
        # Load audio file
        sample_rate, audio = wav.read(self.input_path)

        # Normalize audio
        normalized_audio = audio / np.max(np.abs(audio))

        # Apply compression to audio
        compressed_audio = np.where(np.abs(normalized_audio) > threshold,
                                    threshold +
                                    (np.abs(normalized_audio) - threshold) / ratio,
                                    normalized_audio)

        # Scale audio back to 16-bit signed integers
        scaled_audio = np.int16(compressed_audio * 32767)

        # Save compressed audio to output file
        self.clear_output()
        wav.write(self.output_path, sample_rate, scaled_audio)

    def master_audio(self, automastering=True):
        # Copy original input path to reset input path at the end
        input_path_copy = self.input_path

        # Iterate through steps
        for i, step in enumerate(self.steps):
            print(f'Applying {step}...')

            # Get settings for current step
            step_settings = {}
            calculate_step_settings = getattr(self, f'calculate_{step}_settings', None)
            if automastering and calculate_step_settings:
                step_settings = calculate_step_settings()
            elif step in self.settings:
                step_settings = self.settings[step]

            # Apply current step
            apply_step = getattr(self, f'apply_{step}')
            apply_step(**step_settings)

            # Set input path for next step
            if i == 0:
                self.input_path = self.output_path

            print(f'Finished applying {step}.')

        # Reset input path to original
        self.input_path = input_path_copy