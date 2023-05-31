import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import scipy.signal as signal
import pydub
import pydub.effects
import os

class MasterOfMastering:
    DEFAULT_STEPS = ['normalization', 'equalization']

    DEFAULT_SETTINGS = {
        'equalization': {
            'gain_adjustments': {
                100: 0.5,  # 100 Hz band gain
                1000: 0.2,  # 1000 Hz band gain
                10000: -0.1  # 10000 Hz band gain
            }
        },
        'compression': {
            'threshold': 1.0,
            'ratio': 1.5
        }
    }

    PROFILES = {
        'default': {
            'equalization': {
                # Define frequency bands
                'low_freq_band': 10**2,
                'mid_freq_band': 10**3,
                'high_freq_band': 10**4,
                # Define target energy levels for each frequency band,
                'target_energy_low': 5,
                'target_energy_mid': 4,
                'target_energy_high': 3
            }
        }
    }


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
        # Load equalization profile
        eq_profile = self.profile['equalization']

        low_freq_band = eq_profile['low_freq_band']
        mid_freq_band = eq_profile['mid_freq_band']
        high_freq_band = eq_profile['high_freq_band']
        
        target_energy_low = eq_profile['target_energy_low']
        target_energy_mid = eq_profile['target_energy_mid']
        target_energy_high = eq_profile['target_energy_high']

        # Load audio file
        sample_rate, audio = wav.read(self.input_path)

        # Apply FFT to audio to obtain frequency spectrum
        frequency_bins, segment_spectrum = signal.periodogram(audio, fs=sample_rate, window='hamming')

        # Calculate energy in each frequency band for each segment
        energy_low = np.sum(segment_spectrum[:, (frequency_bins >= low_freq_band) &
                                                      (frequency_bins < mid_freq_band)],
                                    axis=1)
        energy_mid = np.sum(segment_spectrum[:, (frequency_bins >= mid_freq_band) &
                                                      (frequency_bins < high_freq_band)],
                                    axis=1)
        energy_high = np.sum(segment_spectrum[:, (frequency_bins >= high_freq_band) &
                                                        (frequency_bins < high_freq_band * 10)], 
                                    axis=1)
        
        # Calculate mean energy in each frequency band
        mean_energy_low = np.mean(energy_low)
        mean_energy_mid = np.mean(energy_mid)
        mean_energy_high = np.mean(energy_high)

        # Determine gain adjustments based on energy differences
        zero_division_adjustment = 10**-10
        gain_adjustments = {
            low_freq_band: (target_energy_low - mean_energy_low) / (mean_energy_low + zero_division_adjustment),
            mid_freq_band: (target_energy_mid - mean_energy_mid) / (mean_energy_mid + zero_division_adjustment),
            high_freq_band: (target_energy_high - mean_energy_high) / (mean_energy_high + zero_division_adjustment)
        }

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

    def apply_normalization_dep(self, normalization_gain):
        # Load audio file
        sample_rate, audio = wav.read(self.input_path)

        # Normalize audio
        normalized_audio = audio * normalization_gain

        # Scale audio back to 16-bit signed integers
        scaled_audio = np.int16(normalized_audio * 32767)

        # Save normalized audio to output file
        self.clear_output()
        wav.write(self.output_path, sample_rate, scaled_audio)

    
    def apply_normalization(self):
        # Load and normalize audio file with pydub
        audio = pydub.AudioSegment.from_file(self.input_path)
        normalized_audio = pydub.effects.normalize(audio)
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


    # def apply_amplification(self, gain):
    #     # Load audio file
    #     sample_rate, audio = wav.read(self.input_path)

    #     # Amplify audio
    #     amplified_audio = audio * gain

    #     # Scale audio back to 16-bit signed integers
    #     scaled_audio = np.int16(amplified_audio * 32767)

    #     # Save amplified audio to output file
    #     self.clear_output()
    #     wav.write(self.output_path, sample_rate, scaled_audio)


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
        wav.write(output_path, sample_rate, scaled_audio)

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

if __name__ == "__main__":
    # Define input and output paths
    input_path = "audio/input.wav"
    output_path = "audio/output.wav"

    # Create a MasterOfMastering instance
    mom = MasterOfMastering(input_path, output_path)

    # Master audio
    mom.master_audio(automastering=True)
