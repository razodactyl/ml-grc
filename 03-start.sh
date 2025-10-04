#!/bin/bash

# 03-start.sh - Start script for GRC application
# Activates virtual environment and starts/restarts the application

set -e  # Exit on any error

echo "🚀 Starting GRC application..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo "❌ Error: This script must be run from the project root directory."
    exit 1
fi

# Check if virtual environment exists and activate it
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ Error: Virtual environment not found. Please run 00-setup.sh first."
    exit 1
fi

echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Function to check if GRC application is running
is_grc_running() {
    pgrep -f "python.*main.py" > /dev/null 2>&1
    return $?
}

# Function to kill existing GRC processes
kill_grc_processes() {
    echo "🔄 Stopping existing GRC processes..."
    pkill -f "python.*main.py" 2>/dev/null || true
    # Wait a moment for processes to terminate gracefully
    sleep 2
    # Force kill if still running
    pkill -9 -f "python.*main.py" 2>/dev/null || true
}

# Check if GRC is already running
if is_grc_running; then
    echo "🔄 GRC application is already running. Restarting..."
    kill_grc_processes
else
    echo "🆕 Starting new GRC application instance..."
fi

# Start the application
echo "🎯 Launching GRC application..."
cd "$(dirname "$0")"  # Ensure we're in the project root

# Run the main application
python src/grc/main.py &
APP_PID=$!

echo "✅ GRC application started with PID: $APP_PID"
echo ""
echo "📋 Application Status:"
echo "   - Process ID: $APP_PID"
echo "   - Virtual environment: $(which python)"
echo "   - Working directory: $(pwd)"
echo ""
echo "💡 Tips:"
echo "   - To stop the application: Press Ctrl+C or close the GUI window"
echo "   - To restart manually: Run this script again"
echo "   - To run in background: The application is already running in background"
echo ""
echo "🎉 GRC application is now running!"

# Wait for the application process (optional - can be interrupted with Ctrl+C)
wait $APP_PID 2>/dev/null || echo "Application terminated."
