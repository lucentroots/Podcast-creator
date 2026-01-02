# The Podcast creator 🎙️

A Python pipeline that converts Wikipedia articles into natural-sounding 2-minute Hinglish conversation audio files.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- FFmpeg (for audio processing)

**Install FFmpeg:**
```bash
# macOS (using Homebrew)
brew install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 2. Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ELEVENLABS_API_KEY=your-elevenlabs-key-here
   ```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

### 4. Run the Pipeline on Web UI **

```bash
source venv/bin/activate
streamlit run app.py
```

This opens a web interface where you can:
- Paste Wikipedia URLs
- Paste article text directly
- Enter article titles
- Generate and play audio in the browser


## 📦 Project Structure

```
.
├── app.py                      # Streamlit web UI
├── synthetic_radio_host.py    # Main pipeline script
├── requirements.txt            # Python dependencies
├── setup.sh                    # Setup script
├── run_ui.sh                    # Run UI script
├── .env                        # API keys (create this, don't commit)
├── .env.example               # Template for API keys
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## 🔧 Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Make sure you created `.env` file with your keys

**Error: "FFmpeg not found"**
- Install FFmpeg (see Prerequisites)

**Error: "Module not found"**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**Audio sounds robotic?**
- Try adjusting `stability` and `similarity_boost` in `text_to_speech_elevenlabs()`
- Experiment with different voice IDs from ElevenLabs


