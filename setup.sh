#!/bin/bash

# Setup script for Synthetic Radio Host Pipeline

echo "🎙️  Setting up Synthetic Radio Host Pipeline..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check FFmpeg
echo ""
echo "Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "⚠ FFmpeg not found. Please install it:"
    echo "   macOS: brew install ffmpeg"
    echo "   Or download from: https://ffmpeg.org/download.html"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file template..."
    cat > .env << EOF
# Add your API keys here
OPENAI_API_KEY=your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
EOF
    echo "✓ Created .env file. Please edit it and add your API keys!"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the script: python synthetic_radio_host.py"

