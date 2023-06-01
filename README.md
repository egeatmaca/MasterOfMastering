# MasterOfMastering
A Tool for Automated Song Mastering

## Description
MasterOfMastering is a tool for automated song mastering. It calculates effect parameters and applies effects based on pre-specified profiles. \
*** It only supports vaw files for now.

## Command Line Interface (CLI)
Command line interface is a convenient way to use the tool. It is available for Linux and Mac OS.

### Prerequisites
- Python
- Pip

### Setup
1. Clone the repository where you want to install the tool
2. Run `/bin/sh setup.sh` in the root directory of the repository

### Usage

#### Master an audio file
Run `masterofmastering -i <input path> -o <output path> -p <profile name>`.

#### List available profiles
Run `masterofmastering -l`.

#### Parameters
- `-i` or `--input`: Path for the input audio file
- `-o` or `--output`: Path for the output audio file
- `-p` or `--profile`: Name of the profile to be used

## Running the code

### With Docker

#### Prerequisites
- Docker
- Docker Compose

#### Steps
1. Clone the repository
2. Edit parameters in the Dockerfile command according to your needs. \
Replace `audio/input.vaw` with the path for the input audio file. \
Replace `audio/output.vaw` with the path for the output audio file. \
Replace `default` with the profile name.
3. Run `docker compose up` in the root directory of the repository

### With Python and Pip

#### Prerequisites
- Python
- Pip

#### Steps
1. Clone the repository
2. Run `pip install -r requirements.txt` in the root directory of the repository
3. Run `python main.py -i <input audio path> -o <output audio path> -p <profile name>` in the root directory of the repository

