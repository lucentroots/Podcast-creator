# 🚀 Quick Start Guide

## Step 1: Run Setup

```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Add API Keys

Edit the `.env` file (created by setup script) and add your keys:

```env
OPENAI_API_KEY=sk-your-actual-key
ELEVENLABS_API_KEY=your-elevenlabs-key
```

## Step 3: Install FFmpeg (if needed)

```bash
brew install ffmpeg
```

## Step 4: Run!

**Option A: Web UI (Recommended) 🎨**
```bash
./run_ui.sh
```
Opens a beautiful web interface where you can:
- Paste Wikipedia URLs
- Paste article text
- Generate and play audio in browser

**Option B: Command Line**
```bash
source venv/bin/activate  # Activate virtual environment
python synthetic_radio_host.py
```

## What It Does

1. ✅ Fetches Wikipedia article about "Mumbai Indians"
2. ✅ Generates Hinglish conversation script using GPT-4o-mini
3. ✅ Converts to audio using ElevenLabs TTS
4. ✅ Saves as `mumbai_indians_conversation.mp3`

## Customize

Edit `synthetic_radio_host.py` and change:
- `wikipedia_title = "Mumbai Indians"` → any Wikipedia article
- `output_filename = "..."` → your desired filename

## Files Created

- `synthetic_radio_host.py` - Main pipeline script
- `requirements.txt` - Dependencies
- `README.md` - Full documentation
- `HINGLISH_PROMPTING_EXPLANATION.md` - 100-word explanation for competition
- `setup.sh` - Automated setup script

## Need Help?

See `SETUP_INSTRUCTIONS.md` for detailed troubleshooting.

