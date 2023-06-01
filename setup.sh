# Get the directory of this script (project directory)
SCRIPT_DIR=$(dirname $(readlink -f "$0"))
echo "Project directory: $SCRIPT_DIR"

# Cd into project directory
cd $SCRIPT_DIR

# Install requirements
pip install -r requirements.txt

# Create terminal command
echo "alias masterofmastering='python3 $SCRIPT_DIR/main.py'" >> ~/.bashrc