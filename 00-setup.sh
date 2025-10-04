#!/bin/bash

# 00-setup.sh - Setup script for ml-grc project
# Creates virtual environment and installs requirements

set -e  # Exit on any error

echo "🚀 Setting up ml-grc project..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Check if virtual environment exists
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_DIR/"
else
    echo "📦 Virtual environment already exists at $VENV_DIR/"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing requirements from requirements.txt..."
pip install -r requirements.txt

# Verify installation
echo "✅ Setup complete! Verifying installation..."
python -c "import numpy, cv2, PIL, PyQt5, scipy; print('All dependencies installed successfully!')"

echo ""
echo "🎉 Setup finished! You can now activate the virtual environment with:"
echo "   source venv/bin/activate"
echo ""
echo "To deactivate, simply run: deactivate"
