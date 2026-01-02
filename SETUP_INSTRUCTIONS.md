# Setup Instructions

## Quick Setup (Recommended)

Run the setup script:

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file template
- Check for FFmpeg

## Manual Setup

If the script doesn't work, follow these steps:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install FFmpeg

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 4. Create .env File

Create a file named `.env` in the project root with:

```env
OPENAI_API_KEY=your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

**Get your API keys:**
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

### 5. Run the Script

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the pipeline
python synthetic_radio_host.py
```

## Troubleshooting

**If you get permission errors:**
- Try using `python3` instead of `python`
- Make sure you have write permissions in the directory

**If FFmpeg is not found:**
- Install it using Homebrew: `brew install ffmpeg`
- Or download from the official website

**If packages fail to install:**
- Make sure your virtual environment is activated
- Try upgrading pip: `pip install --upgrade pip`
- Check your internet connection

