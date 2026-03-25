#!/bin/bash

# Exit on error
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

# Determine base python command
if command -v python3 &> /dev/null; then
    BASE_PYTHON="python3"
elif command -v python &> /dev/null; then
    BASE_PYTHON="python"
else
    echo "Python 3 was not found. Install Python and add it to PATH."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Creating virtual environment in $VENV_DIR ..."
    $BASE_PYTHON -m venv "$VENV_DIR"
fi

# Check for pycryptodome and install if missing
if ! "$VENV_PYTHON" -c "import Crypto.Cipher" &> /dev/null; then
    echo "Installing dependency: pycryptodome ..."
    "$VENV_PYTHON" -m pip install --upgrade pip
    "$VENV_PYTHON" -m pip install pycryptodome
fi

# Compile the python script
"$VENV_PYTHON" -m py_compile "$SCRIPT_DIR/passwordManager.py"

# Run the requested commands automatically
echo "./passwordManager.py init mAsterPasswrd"
"$VENV_PYTHON" "$SCRIPT_DIR/passwordManager.py" init mAsterPasswrd

echo -e "\n./passwordManager.py put mAsterPasswrd www.fer.hr neprobojnAsifrA"
"$VENV_PYTHON" "$SCRIPT_DIR/passwordManager.py" put mAsterPasswrd www.fer.hr neprobojnAsifrA

echo -e "\n./passwordManager.py get mAsterPasswrd www.fer.hr"
"$VENV_PYTHON" "$SCRIPT_DIR/passwordManager.py" get mAsterPasswrd www.fer.hr

# Disable exit on error for the last command since wrong password might trigger a non-zero exit code
set +e
echo -e "\n./passwordManager.py get wrongPasswrd www.fer.hr"
"$VENV_PYTHON" "$SCRIPT_DIR/passwordManager.py" get wrongPasswrd www.fer.hr
