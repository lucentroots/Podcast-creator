# ============================================================================
# THE SYNTHETIC RADIO HOST - Complete Pipeline (Local Version)
# ============================================================================

import os
import json
import re
from typing import List, Tuple
import requests
import io
from dotenv import load_dotenv

# Configure FFmpeg path for pydub (using imageio-ffmpeg)
FFMPEG_PATH = None
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

# Import pydub and configure
from pydub import AudioSegment
from pydub.effects import normalize

if FFMPEG_PATH:
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffmpeg = FFMPEG_PATH
    AudioSegment.ffprobe = FFMPEG_PATH

# Load environment variables from .env file
load_dotenv()

# Import libraries
import wikipediaapi
from openai import OpenAI

# ElevenLabs - try different import methods
ELEVENLABS_AVAILABLE = False
ELEVENLABS_OLD_API = False
elevenlabs_generate = None

try:
    # Try new API (v1.0.0+)
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    ELEVENLABS_OLD_API = False
except ImportError:
    try:
        # Try older API
        from elevenlabs import generate, set_api_key
        elevenlabs_generate = generate
        ELEVENLABS_AVAILABLE = True
        ELEVENLABS_OLD_API = True
    except ImportError:
        ELEVENLABS_AVAILABLE = False
        ELEVENLABS_OLD_API = False

# ============================================================================
# CONFIGURATION - Load from environment variables
# ============================================================================

from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
ENV_PATH = SCRIPT_DIR / ".env"

# Initialize clients lazily (only when needed, not at import time)
groq_client = None
openai_client = None
elevenlabs_client = None

def get_api_key(key_name: str) -> str:
    """Get API key from environment, reloading .env if needed."""
    # Reload .env from the script's directory to get the latest values
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    else:
        # Try current directory as fallback
        load_dotenv(override=True)
    
    return os.getenv(key_name)

def get_groq_client():
    """Get or create Groq client lazily (uses OpenAI-compatible API)."""
    global groq_client
    if groq_client is None:
        api_key = get_api_key("GROQ_API_KEY")
        if api_key:
            try:
                # Groq uses OpenAI-compatible API
                groq_client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
    return groq_client

def get_openai_client():
    """Get or create OpenAI client lazily (for TTS)."""
    global openai_client
    if openai_client is None:
        api_key = get_api_key("OPENAI_API_KEY")
        if api_key:
            try:
                openai_client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    return openai_client

def get_elevenlabs_client():
    """Get or create ElevenLabs client lazily."""
    global elevenlabs_client
    api_key = get_api_key("ELEVENLABS_API_KEY")
    if elevenlabs_client is None and api_key and ELEVENLABS_AVAILABLE:
        try:
            if not ELEVENLABS_OLD_API:
                # New API (v1.0.0+)
                elevenlabs_client = ElevenLabs(api_key=api_key)
            else:
                # Old API
                from elevenlabs import set_api_key
                set_api_key(api_key)
        except Exception as e:
            print(f"Warning: Could not initialize ElevenLabs client: {e}")
    return elevenlabs_client

def get_elevenlabs_api_key():
    """Get ElevenLabs API key."""
    return get_api_key("ELEVENLABS_API_KEY")

# ============================================================================
# STEP 1: FETCH WIKIPEDIA ARTICLE
# ============================================================================

def fetch_wikipedia_article(title: str, max_chars: int = 2000) -> str:
    """Fetches and returns Wikipedia article text."""
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent='SyntheticRadioHost/1.0 (https://github.com/synthetic-radio-host; contact@example.com)',
            language='en'
        )
        page = wiki_wiki.page(title)
        
        if not page.exists():
            return f"Article '{title}' not found. Please check the title."
        
        text = page.text
        
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        print(f"✓ Fetched Wikipedia article: {title}")
        print(f"  Length: {len(text)} characters")
        return text
    
    except Exception as e:
        print(f"✗ Error fetching Wikipedia article: {e}")
        return None

# ============================================================================
# STEP 2: GENERATE HINGLISH CONVERSATION SCRIPT
# ============================================================================

def create_conversation_prompt(article_text: str, language_type: str = "Hinglish") -> str:
    """Creates the prompt for generating a natural conversation script."""
    
    if language_type == "Tanglish":
        prompt = f"""You are creating a natural, informative conversational script for a 2-minute radio show segment.

TOPIC: {article_text[:1500]}...

REQUIREMENTS:
1. Create a DEEP, INFORMATIVE conversation between two friends: Person A and Person B
2. Use TANGLISH - naturally mix Tamil and English words (like real Tamil conversations)
3. Make it informative and engaging - discuss key facts, details, and insights from the article
4. Include MINIMAL natural speech patterns (use sparingly, maximum 2-3 times total):
   - Occasional: "appadiya", "seri", "correct", "exactly"
   - Rare thinking: "let me think", "paathu"
   - Very rare laughter: [laughs] (only if genuinely funny)
5. Focus on CONTENT: Share specific details, numbers, facts, and insights from the article
6. Make it DEEPER: Don't just summarize - discuss implications, interesting aspects, comparisons
7. Duration: Approximately 2 minutes when spoken (aim for 350-450 words total)
8. Format: Mark each speaker clearly as "Person A:" or "Person B:"
9. Make it engaging, informative, and conversational - like two knowledgeable friends discussing

EXAMPLE OF GOOD TANGLISH (informative, minimal fillers):
Person A: "I read about Mumbai Indians - they won 5 IPL titles, which is the most by any team."
Person B: "Correct! And Rohit Sharma has been their captain since 2013. The team's strategy has been really interesting."
Person A: "Yeah, they focus on building a strong core team and then add specific players for each season."
Person B: "That's a smart approach. Their scouting system is also one of the best in the league."

Now create a similar 2-minute INFORMATIVE conversation script about the topic above:"""
    
    else:  # Hinglish
        prompt = f"""You are creating a natural, informative conversational script for a 2-minute radio show segment.

TOPIC: {article_text[:1500]}...

REQUIREMENTS:
1. Create a DEEP, INFORMATIVE conversation between two friends: Person A and Person B
2. Use HINGLISH - naturally mix Hindi and English words (like real Indian conversations)
3. Make it informative and engaging - discuss key facts, details, and insights from the article
4. Include MINIMAL natural speech patterns (use sparingly, maximum 2-3 times total):
   - Occasional: "achcha", "haan", "exactly", "sahi hai"
   - Rare thinking: "let me think", "dekho"
   - Very rare: "yaar" (only once or twice), "arre" (rarely)
   - Very rare laughter: [laughs] (only if genuinely funny)
5. Focus on CONTENT: Share specific details, numbers, facts, and insights from the article
6. Make it DEEPER: Don't just summarize - discuss implications, interesting aspects, comparisons
7. Duration: Approximately 2 minutes when spoken (aim for 350-450 words total)
8. Format: Mark each speaker clearly as "Person A:" or "Person B:"
9. Make it engaging, informative, and conversational - like two knowledgeable friends discussing

EXAMPLE OF GOOD HINGLISH (informative, minimal fillers):
Person A: "Mumbai Indians have won 5 IPL titles, which is the most by any team in the league."
Person B: "Haan, and Rohit Sharma has been their captain since 2013. Their strategy has been really interesting."
Person A: "They focus on building a strong core team and then add specific players for each season."
Person B: "Exactly! Their scouting system is also one of the best - they find talent from smaller cities."

Now create a similar 2-minute INFORMATIVE conversation script about the topic above:"""

    return prompt

def generate_conversation_script(article_text: str, language_type: str = "Hinglish") -> str:
    """Uses Groq (Llama) to generate the conversation script."""
    client = get_groq_client()
    if not client:
        raise ValueError("Groq client not initialized. Please set GROQ_API_KEY in .env file")
    
    try:
        prompt = create_conversation_prompt(article_text, language_type)
        
        print("🤖 Generating conversation script with Groq (Llama)...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast, high-quality open-source model
            messages=[
                {"role": "system", "content": "You are an expert at creating natural, conversational scripts in Hinglish (Hindi-English mix) for radio shows."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )
        
        script = response.choices[0].message.content
        print("✓ Script generated successfully!")
        print(f"  Script length: {len(script)} characters")
        
        return script
    
    except Exception as e:
        print(f"✗ Error generating script: {e}")
        return None

def parse_script(script: str) -> List[Tuple[str, str]]:
    """Parses the script into speaker segments."""
    segments = []
    current_speaker = None
    current_text = []
    
    lines = script.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("Person A:"):
            if current_speaker and current_text:
                segments.append((current_speaker, ' '.join(current_text)))
            current_speaker = "Person A"
            current_text = [line.replace("Person A:", "").strip()]
        
        elif line.startswith("Person B:"):
            if current_speaker and current_text:
                segments.append((current_speaker, ' '.join(current_text)))
            current_speaker = "Person B"
            current_text = [line.replace("Person B:", "").strip()]
        
        else:
            if current_speaker:
                current_text.append(line)
    
    if current_speaker and current_text:
        segments.append((current_speaker, ' '.join(current_text)))
    
    return segments

# ============================================================================
# STEP 3: TEXT-TO-SPEECH CONVERSION
# ============================================================================

def text_to_speech_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM", 
                              stability: float = 0.5, similarity_boost: float = 0.75) -> bytes:
    """Converts text to speech using ElevenLabs API."""
    api_key = get_elevenlabs_api_key()
    if not api_key:
        raise ValueError("ElevenLabs API key not set. Please set ELEVENLABS_API_KEY in .env file")
    
    try:
        # Try using HTTP API directly (most compatible)
        import json
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        # Check for errors and provide detailed messages
        if response.status_code != 200:
            error_msg = f"ElevenLabs API error (Status {response.status_code})"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    error_msg += f": {error_data['detail']}"
                elif 'message' in error_data:
                    error_msg += f": {error_data['message']}"
            except:
                error_msg += f": {response.text[:200]}"
            
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        
        response.raise_for_status()
        return response.content
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error connecting to ElevenLabs: {str(e)}"
        print(f"✗ {error_msg}")
        # Don't fallback on network errors, raise immediately
        raise Exception(error_msg)
    except Exception as e:
        error_msg = str(e)
        print(f"✗ ElevenLabs TTS error: {error_msg}")
        
        # Fallback to SDK if available
        if ELEVENLABS_AVAILABLE:
            try:
                if ELEVENLABS_OLD_API and elevenlabs_generate:
                    from elevenlabs import Voice, VoiceSettings
                    audio = elevenlabs_generate(
                        text=text,
                        voice=Voice(
                            voice_id=voice_id,
                            settings=VoiceSettings(
                                stability=stability,
                                similarity_boost=similarity_boost,
                                style=0.5,
                                use_speaker_boost=True
                            )
                        )
                    )
                    if hasattr(audio, 'read'):
                        return audio.read()
                    return bytes(audio) if not isinstance(audio, bytes) else audio
                elif elevenlabs_client:
                    audio = elevenlabs_client.generate(
                        text=text,
                        voice=voice_id,
                        model_id="eleven_multilingual_v2"
                    )
                    if hasattr(audio, 'read'):
                        return audio.read()
                    return bytes(audio) if not isinstance(audio, bytes) else audio
            except Exception as e2:
                print(f"✗ ElevenLabs SDK fallback error: {e2}")
                # Re-raise with original error message
                raise Exception(f"ElevenLabs TTS failed: {error_msg}. SDK fallback also failed: {str(e2)}")
        
        # If we get here, all methods failed
        import traceback
        traceback.print_exc()
        raise Exception(f"ElevenLabs TTS failed: {error_msg}")

def text_to_speech_openai(text: str, voice: str = "alloy") -> bytes:
    """Alternative: Uses OpenAI TTS."""
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY in .env file")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0
        )
        return response.content
    except Exception as e:
        print(f"✗ OpenAI TTS error: {e}")
        return None

def generate_audio_for_segments(segments: List[Tuple[str, str]], 
                                use_elevenlabs: bool = True,
                                voice_a_id: str = "21m00Tcm4TlvDq8ikWAM",
                                voice_b_id: str = "pNInz6obpgDQGcFmaJgB",
                                openai_voice_a: str = "nova",
                                openai_voice_b: str = "onyx") -> List[bytes]:
    """Generates audio for each segment. Returns list of MP3 bytes.
    
    Args:
        segments: List of (speaker, dialogue) tuples
        use_elevenlabs: If True, use ElevenLabs TTS, else use OpenAI TTS
        voice_a_id: ElevenLabs voice ID for Person A
        voice_b_id: ElevenLabs voice ID for Person B
        openai_voice_a: OpenAI voice name for Person A
        openai_voice_b: OpenAI voice name for Person B
    
    Raises:
        Exception: If audio generation fails with detailed error message
    """
    audio_segments = []
    failed_segments = []
    
    voice_a = voice_a_id
    voice_b = voice_b_id
    
    print(f"🎤 Generating audio for {len(segments)} segments...")
    
    for i, (speaker, dialogue) in enumerate(segments):
        print(f"  Processing segment {i+1}/{len(segments)}: {speaker}")
        
        clean_dialogue = dialogue.replace("[laughs]", "").replace("[laugh]", "").strip()
        
        if not clean_dialogue:
            print(f"  ⚠ Warning: Segment {i+1} is empty, skipping")
            continue
        
        try:
            if use_elevenlabs:
                voice_id = voice_a if speaker == "Person A" else voice_b
                audio_bytes = text_to_speech_elevenlabs(clean_dialogue, voice_id=voice_id)
            else:
                voice = openai_voice_a if speaker == "Person A" else openai_voice_b
                audio_bytes = text_to_speech_openai(clean_dialogue, voice=voice)
            
            if audio_bytes and len(audio_bytes) > 0:
                audio_segments.append(audio_bytes)
                print(f"  ✓ Generated {len(audio_bytes)} bytes for segment {i+1}")
            else:
                failed_segments.append(i+1)
                print(f"  ⚠ Warning: Failed to generate audio for segment {i+1} - returned empty")
        except Exception as e:
            failed_segments.append(i+1)
            print(f"  ✗ Error generating segment {i+1}: {str(e)}")
            # Continue with other segments, but track failures
    
    if len(audio_segments) == 0:
        error_msg = "All audio segments failed to generate."
        if failed_segments:
            error_msg += f" Failed segments: {failed_segments}"
        raise Exception(error_msg)
    
    if len(failed_segments) > 0:
        print(f"  ⚠ Warning: {len(failed_segments)} segments failed, but {len(audio_segments)} succeeded")
    
    return audio_segments

# ============================================================================
# STEP 4: COMBINE AUDIO AND EXPORT
# ============================================================================

def combine_and_export_audio(audio_segments: List[bytes], 
                             output_filename: str = "hinglish_conversation.mp3") -> str:
    """Combines all audio segments with volume normalization and exports as MP3."""
    if not audio_segments:
        print("✗ No audio segments to combine!")
        return None
    
    print("🔊 Combining and normalizing audio segments...")
    
    try:
        # Try to use pydub for volume normalization
        combined_audio_seg = AudioSegment.empty()
        
        for audio_bytes in audio_segments:
            audio_seg = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            # Normalize each segment to same volume level
            audio_seg = audio_seg.normalize()
            combined_audio_seg += audio_seg
            # Add small pause between segments
            combined_audio_seg += AudioSegment.silent(duration=300)
        
        # Final normalization to ensure consistent volume
        combined_audio_seg = normalize(combined_audio_seg)
        
        # Export
        combined_audio_seg.export(output_filename, format="mp3")
        
        duration_seconds = len(combined_audio_seg) / 1000.0
        print(f"✓ Audio exported: {output_filename}")
        print(f"  File size: {os.path.getsize(output_filename) / 1024:.1f} KB")
        print(f"  Duration: {duration_seconds:.1f} seconds ({duration_seconds/60:.1f} minutes)")
        
        return output_filename
        
    except Exception as e:
        print(f"⚠ Volume normalization failed, using simple concatenation: {e}")
        # Fallback: simple concatenation
        combined_audio = b''.join(audio_segments)
        with open(output_filename, 'wb') as f:
            f.write(combined_audio)
        
        estimated_duration = len(combined_audio) / 10000
        print(f"✓ Audio exported: {output_filename}")
        print(f"  File size: {len(combined_audio) / 1024:.1f} KB")
        print(f"  Estimated duration: ~{estimated_duration:.0f} seconds")
        
        return output_filename

# ============================================================================
# MAIN PIPELINE FUNCTION
# ============================================================================

def create_synthetic_radio_host(wikipedia_title: str, 
                                output_filename: str = "hinglish_conversation.mp3",
                                use_elevenlabs: bool = True) -> str:
    """Main pipeline function."""
    print("=" * 60)
    print("🎙️  THE SYNTHETIC RADIO HOST - Starting Pipeline")
    print("=" * 60)
    
    article_text = fetch_wikipedia_article(wikipedia_title)
    if not article_text:
        return None
    
    script = generate_conversation_script(article_text)
    if not script:
        return None
    
    print("\n📝 Generated Script:")
    print("-" * 60)
    print(script)
    print("-" * 60)
    
    segments = parse_script(script)
    print(f"\n✓ Parsed into {len(segments)} segments")
    
    audio_segments = generate_audio_for_segments(segments, use_elevenlabs=use_elevenlabs)
    if not audio_segments:
        return None
    
    output_path = combine_and_export_audio(audio_segments, output_filename)
    
    print("\n" + "=" * 60)
    print("✅ Pipeline Complete!")
    print("=" * 60)
    
    return output_path

# ============================================================================
# RUN THE PIPELINE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    wikipedia_title = "Mumbai Indians"
    
    output_file = create_synthetic_radio_host(
        wikipedia_title=wikipedia_title,
        output_filename="mumbai_indians_conversation.mp3",
        use_elevenlabs=True
    )
    
    if output_file:
        print(f"\n🎉 Success! Audio file saved as: {output_file}")
    else:
        print("\n❌ Pipeline failed. Check the error messages above.")

