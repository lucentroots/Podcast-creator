# 🎙️ UI Guide - The Synthetic Radio Host

## Quick Start

1. **Run the UI:**
   ```bash
   ./run_ui.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

2. **Open your browser:**
   - The UI will automatically open at `http://localhost:8501`
   - If not, copy the URL shown in the terminal

## Using the UI

### Input Methods

The UI supports three ways to input article content:

#### 1. 📄 Wikipedia URL
- Paste a Wikipedia article URL
- Example: `https://en.wikipedia.org/wiki/Mumbai_Indians`
- The app will automatically extract the article title and fetch the content

#### 2. 📝 Paste Article Text
- Copy and paste the entire article text directly
- Works with any text content (not just Wikipedia)
- Automatically truncates to 2000 characters for efficiency

#### 3. 📖 Article Title
- Enter the exact Wikipedia article title
- Example: `Mumbai Indians`
- The app will fetch the article from Wikipedia

### Settings

**TTS Provider:**
- **ElevenLabs (Better Quality)**: Higher quality, more natural voices (recommended)
- **OpenAI TTS (Cheaper)**: Lower cost alternative

**API Keys:**
- Check the sidebar to verify your API keys are loaded
- Keys are loaded from your `.env` file

### Generating Audio

1. Choose your input method
2. Enter the article content (URL, text, or title)
3. Click **"🎙️ Generate Conversation Audio"**
4. Wait for processing (progress bar shows status)
5. View the generated script in the expandable section
6. Play the audio using the built-in player
7. Download the MP3 file using the download button

## Features

✅ **Real-time Progress**: See each step of the pipeline
✅ **Script Preview**: View the generated Hinglish conversation before audio generation
✅ **Built-in Audio Player**: Listen to your audio directly in the browser
✅ **Download Option**: Save the MP3 file to your computer
✅ **Error Handling**: Clear error messages if something goes wrong

## Troubleshooting

**UI won't start:**
- Make sure virtual environment is activated
- Install Streamlit: `pip install streamlit`
- Check Python version: `python3 --version` (needs 3.9+)

**API Key errors:**
- Check that `.env` file exists in the project root
- Verify keys are correctly formatted (no quotes, no spaces)
- Restart the UI after adding keys

**Audio generation fails:**
- Check your API key balances
- Verify internet connection
- Try using OpenAI TTS instead of ElevenLabs

**Audio player not working:**
- Check browser console for errors
- Try downloading the file instead
- Ensure MP3 file was generated successfully

## Tips

1. **For best results**: Use Wikipedia URLs or article titles (more structured content)
2. **For speed**: Use OpenAI TTS (faster and cheaper)
3. **For quality**: Use ElevenLabs (more natural voices)
4. **For testing**: Start with shorter articles or paste just a paragraph
5. **For competition**: Use the script preview to verify Hinglish quality before generating audio

## Keyboard Shortcuts

- `Ctrl+C` in terminal: Stop the UI server
- `R` in Streamlit: Rerun the app
- `C` in Streamlit: Clear cache

