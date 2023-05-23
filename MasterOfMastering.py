import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import pydub
import pydub.effects

class MasterOfMastering:
    DEFAULT_STEPS = ['normalization', 'equalization', 'compression']
    DEFAULT_SETTINGS = {
        'normalization': { 

        },
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

    def __init__(self, input_path, output_path, steps=DEFAULT_STEPS, settings=DEFAULT_SETTINGS):
        self.input_path = input_path
        self.output_path = output_path
        self.steps = steps
        self.settings = settings

        # Copy audio from input file to output file
        wav.write(output_path, *wav.read(input_path))

        # Fill in missing settings with default settings
        for step in steps:
            if step not in settings.keys() and step in self.DEFAULT_SETTINGS.keys():
                settings[step] = self.DEFAULT_SETTINGS[step]
    
    def calculate_equalization_settings(self):
        # Define frequency bands
        low_freq_band = 10**2    
        mid_freq_band = 10**3  
        high_freq_band = 10**4

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
        target_energy_low = 0.4  # Example target energy level for low-frequency band
        target_energy_mid = 0.3  # Example target energy level for mid-frequency band
        target_energy_high = 0.1  # Example target energy level for high-frequency band

        gain_adjustments = {
            low_freq_band: target_energy_low - mean_energy_low,
            mid_freq_band: target_energy_mid - mean_energy_mid,
            high_freq_band: target_energy_high - mean_energy_high
        }

        for band, gain in gain_adjustments.items():
            if gain < -1:
                gain_adjustments[band] = -1
            elif gain > 1:
                gain_adjustments[band] = 1

        # Set and return equalization settings
        settings = {'gain_adjustments': gain_adjustments}
        self.settings['equalization'] = settings
        return settings

    def calculate_compression_settings(self):
        # TODO: Implement compression settings calculation
        return self.DEFAULT_SETTINGS['compression']

    def apply_normalization_dep(self, normalization_gain):
        # Load audio file
        sample_rate, audio = wav.read(self.input_path)

        # Normalize audio
        normalized_audio = audio * normalization_gain

        # Scale audio back to 16-bit signed integers
        scaled_audio = np.int16(normalized_audio * 32767)

        # Save normalized audio to output file
        wav.write(self.output_path, sample_rate, scaled_audio)

    
    def apply_normalization(self):
        # Load and normalize audio file with pydub
        audio = pydub.AudioSegment.from_file(self.input_path)
        normalized_audio = pydub.effects.normalize(audio)
        normalized_audio.export(self.output_path, format="wav")

    def apply_equalization(self, gain_adjustments):
        # Load audio file
        audio = pydub.AudioSegment.from_file(self.input_path)

        # Apply equalization settings to audio
        eq_audio = audio
        for band, gain in gain_adjustments.items():
            eq_audio = eq_audio + pydub.effects.low_pass_filter(eq_audio, band)
            eq_audio = pydub.effects.high_pass_filter(eq_audio, band)
            eq_audio = pydub.effects.pan(eq_audio, gain)

        # Export equalized audio to output file
        eq_audio.export(self.output_path, format="wav")

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
        wav.write(output_path, sample_rate, scaled_audio)

    def master_audio(self):
        input_path_copy = self.input_path

        for i, step in enumerate(self.steps):
            step_settings = {}

            calculate_step_settings = getattr(self, f'calculate_{step}_settings', None)
            if calculate_step_settings:
                step_settings = calculate_step_settings()

            apply_step = getattr(self, f'apply_{step}')
            apply_step(**step_settings)

            if i == 0:
                self.input_path = self.output_path

        self.input_path = input_path_copy

if __name__ == "__main__":
    # Define input and output paths
    input_path = "audio/input.wav"
    output_path = "audio/output.wav"

    # Create a MasterOfMastering instance
    mom = MasterOfMastering(input_path, output_path)

    # Master audio
    mom.master_audio()
