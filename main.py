from MasterOfMastering import MasterOfMastering

if __name__ == "__main__":
    # Define input and output paths
    input_path = "audio/input.wav"
    output_path = "audio/output.wav"

    # Create a MasterOfMastering instance
    mom = MasterOfMastering(input_path, output_path, profile='default')

    # Master audio
    mom.master_audio(automastering=True)