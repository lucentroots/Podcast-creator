#!/bin/bash

# Run Streamlit UI for Synthetic Radio Host

echo "🎙️  Starting Synthetic Radio Host UI..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠ Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing Streamlit..."
    pip install streamlit
fi

# Run Streamlit app
echo "🚀 Launching UI..."
streamlit run app.py

