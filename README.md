# The Synthetic Radio Host 🎙️

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

### 4. Run the Pipeline

**Option A: Web UI (Recommended)**
```bash
./run_ui.sh
```

Or manually:
```bash
source venv/bin/activate
streamlit run app.py
```

This opens a web interface where you can:
- Paste Wikipedia URLs
- Paste article text directly
- Enter article titles
- Generate and play audio in the browser

**Option B: Command Line**
```bash
python synthetic_radio_host.py
```

This will:
1. Fetch the Wikipedia article about "Mumbai Indians"
2. Generate a Hinglish conversation script
3. Convert it to audio using TTS
4. Save as `mumbai_indians_conversation.mp3`

## 📝 Customization

Edit the script to change:
- **Wikipedia article**: Change `wikipedia_title` in the `__main__` section
- **Output filename**: Change `output_filename` parameter
- **TTS provider**: Set `use_elevenlabs=False` to use OpenAI TTS instead

## 🎯 Competition Deliverables

1. **Python Script**: `synthetic_radio_host.py` (ready to share)
2. **MP3 Sample**: Generated in the same directory
3. **100-word Explanation**: See `HINGLISH_PROMPTING_EXPLANATION.md`

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

## 💡 Tips for Winning

1. **Iterate on the prompt**: The Hinglish prompt in `create_hinglish_prompt()` is key - test different variations
2. **Voice selection**: Try different ElevenLabs voices for more natural sound
3. **Pacing**: Adjust pause duration between speakers (currently 500ms)
4. **Test with different articles**: Try various Wikipedia topics to ensure robustness

## 📊 Cost Estimates

- OpenAI GPT-4o-mini: ~$0.01-0.02 per script
- ElevenLabs TTS: ~$0.10-0.20 per 2-minute audio (free tier: 10,000 chars/month)
- OpenAI TTS: ~$0.03-0.06 per 2-minute audio (cheaper alternative)

