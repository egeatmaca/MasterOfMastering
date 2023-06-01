from MasterOfMastering import MasterOfMastering
from config import PROFILES
from argparse import ArgumentParser
    

if __name__ == "__main__":
    # Create an argument parser
    parser = ArgumentParser(description="Master audio files")
    # Add arguments
    parser.add_argument("-i", "--input", help="Path for the input audio file")
    parser.add_argument("-o", "--output", help="Path for the output audio file")
    parser.add_argument("-p", "--profile", help="Name of the profile to use", default="default")
    parser.add_argument("-l", "--list", help="List available profiles", action="store_true")
    # Parse arguments
    args = parser.parse_args()

    if args.list:
        # List profiles
        print("Available profiles:")
        for profile in PROFILES:
            print(f" - {profile}")
    elif args.input and args.output:
        # Master audio
        args.profile = args.profile if args.profile in PROFILES else "default"
        mom = MasterOfMastering(args.input, args.output, profile=args.profile)
        mom.master_audio(automastering=True)
    else:
        parser.print_help()
        # Show help
