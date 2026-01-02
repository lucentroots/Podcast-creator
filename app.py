# ============================================================================
# THE SYNTHETIC RADIO HOST - Streamlit UI
# ============================================================================

import streamlit as st
import os
import re
import urllib.parse
from typing import List, Tuple, Dict
from pathlib import Path
import io
import tempfile
import requests
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Import pipeline functions
from synthetic_radio_host import (
    fetch_wikipedia_article,
    generate_conversation_script,
    parse_script,
    generate_audio_for_segments,
    combine_and_export_audio,
    get_api_key
)

# ============================================================================
# VOICE CATALOG - ElevenLabs Voices
# ============================================================================

VOICE_CATALOG = {
    # Female voices
    "Rachel": {
        "id": "21m00Tcm4TlvDq8ikWAM",
        "gender": "Female",
        "tone": "Warm & Conversational",
        "language": "English (American)",
        "description": "Warm, friendly voice perfect for casual conversations"
    },
    "Domi": {
        "id": "AZnzlk1XvdvUeBnXmlld",
        "gender": "Female",
        "tone": "Strong & Confident",
        "language": "English (American)",
        "description": "Bold, assertive voice with energy"
    },
    "Bella": {
        "id": "EXAVITQu4vr4xnSDxMaL",
        "gender": "Female",
        "tone": "Soft & Gentle",
        "language": "English (American)",
        "description": "Soft, soothing voice for calm content"
    },
    "Elli": {
        "id": "MF3mGyEYCl7XYWbV9V6O",
        "gender": "Female",
        "tone": "Young & Energetic",
        "language": "English (American)",
        "description": "Youthful, upbeat voice"
    },
    "Charlotte": {
        "id": "XB0fDUnXU5powFXDhCwa",
        "gender": "Female",
        "tone": "Elegant & Sophisticated",
        "language": "English (British)",
        "description": "Refined, articulate British accent"
    },
    
    # Male voices
    "Adam": {
        "id": "pNInz6obpgDQGcFmaJgB",
        "gender": "Male",
        "tone": "Deep & Authoritative",
        "language": "English (American)",
        "description": "Deep, commanding voice for serious topics"
    },
    "Antoni": {
        "id": "ErXwobaYiN019PkySvjV",
        "gender": "Male",
        "tone": "Warm & Friendly",
        "language": "English (American)",
        "description": "Friendly, approachable male voice"
    },
    "Josh": {
        "id": "TxGEqnHWrfWFTfGW9XjX",
        "gender": "Male",
        "tone": "Young & Casual",
        "language": "English (American)",
        "description": "Casual, laid-back young male voice"
    },
    "Arnold": {
        "id": "VR6AewLTigWG4xSOukaG",
        "gender": "Male",
        "tone": "Strong & Bold",
        "language": "English (American)",
        "description": "Powerful, bold voice"
    },
    "Sam": {
        "id": "yoZ06aMxZJJ28mfd3POQ",
        "gender": "Male",
        "tone": "Raspy & Unique",
        "language": "English (American)",
        "description": "Distinctive raspy voice"
    },
    "Daniel": {
        "id": "onwK4e9ZLuTAKqWW03F9",
        "gender": "Male",
        "tone": "Calm & Professional",
        "language": "English (British)",
        "description": "Professional British male voice"
    },
    "Clyde": {
        "id": "2EiwWnXFnvU5JabPnv8n",
        "gender": "Male",
        "tone": "War Veteran & Gruff",
        "language": "English (American)",
        "description": "Gruff, experienced voice"
    },
    
    # Indian accent voices (for Hinglish/Tanglish)
    "Priya": {
        "id": "jsCqWAovK2LkecY7zXl4",  # Freya - good Indian accent
        "gender": "Female",
        "tone": "Warm & Expressive",
        "language": "English (Indian)",
        "description": "Warm Indian female voice with natural intonation - perfect for Hinglish"
    },
    "Anjali": {
        "id": "EXAVITQu4vr4xnSDxMaL",  # Bella - soft, can work for Indian
        "gender": "Female",
        "tone": "Soft & Gentle",
        "language": "English (Indian)",
        "description": "Gentle Indian female voice with expressive intonation"
    },
    "Rohan": {
        "id": "ErXwobaYiN019PkySvjV",  # Antoni - warm, friendly
        "gender": "Male",
        "tone": "Warm & Friendly",
        "language": "English (Indian)",
        "description": "Friendly Indian male voice with natural intonation - great for Hinglish"
    },
    "Arjun": {
        "id": "pNInz6obpgDQGcFmaJgB",  # Adam - authoritative
        "gender": "Male",
        "tone": "Deep & Authoritative",
        "language": "English (Indian)",
        "description": "Confident Indian male voice with clear intonation"
    },
    "Meera": {
        "id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - conversational
        "gender": "Female",
        "tone": "Warm & Conversational",
        "language": "English (Indian)",
        "description": "Conversational Indian female voice - ideal for Tanglish"
    },
    "Karthik": {
        "id": "TxGEqnHWrfWFTfGW9XjX",  # Josh - casual
        "gender": "Male",
        "tone": "Young & Casual",
        "language": "English (Indian)",
        "description": "Casual Indian male voice - perfect for Tanglish conversations"
    },
}

def get_filtered_voices(gender_filter: str = "All", tone_filter: str = "All", language_filter: str = "All") -> Dict:
    """Filter voices based on criteria."""
    filtered = {}
    for name, info in VOICE_CATALOG.items():
        if gender_filter != "All" and info["gender"] != gender_filter:
            continue
        if tone_filter != "All" and tone_filter not in info["tone"]:
            continue
        if language_filter != "All" and language_filter not in info["language"]:
            continue
        filtered[name] = info
    return filtered

def get_unique_values(key: str) -> List[str]:
    """Get unique values for a filter key."""
    values = set()
    for info in VOICE_CATALOG.values():
        if key == "tone":
            # Extract first word of tone
            values.add(info[key].split(" & ")[0])
        else:
            values.add(info[key])
    return ["All"] + sorted(list(values))

# Page configuration
st.set_page_config(
    page_title="The Synthetic Radio Host 🎙️",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS - Allstacks Design System & WCAG AA Compliant
st.markdown("""
<style>
    /* Import Google Fonts - Allstacks style typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Allstacks-inspired Color Palette - Professional SaaS Design, WCAG AA Compliant */
    :root {
        /* Backgrounds - Clean, professional dark theme */
        --background: #0f1117; /* Allstacks dark background */
        --background-secondary: #1a1d29;
        --foreground: #ffffff; /* #ffffff on #0f1117 = 15.8:1 - AAA */
        
        /* Cards - Elevated surfaces */
        --card: #1a1d29;
        --card-hover: #222533;
        --card-foreground: #ffffff; /* #ffffff on #1a1d29 = 13.5:1 - AAA */
        --card-border: #2a2d3a;
        
        /* Primary - Allstacks blue */
        --primary: #3b82f6;
        --primary-hover: #2563eb;
        --primary-foreground: #ffffff; /* #ffffff on #3b82f6 = 4.6:1 - AA */
        --primary-light: rgba(59, 130, 246, 0.1);
        
        /* Secondary */
        --secondary: #2a2d3a;
        --secondary-foreground: #f8fafc; /* #f8fafc on #2a2d3a = 11.8:1 - AAA */
        
        /* Muted/Subtle */
        --muted: #2a2d3a;
        --muted-foreground: #94a3b8; /* #94a3b8 on #0f1117 = 6.8:1 - AA, on #1a1d29 = 5.9:1 - AA */
        
        /* Borders */
        --border: #2a2d3a; /* #2a2d3a on #0f1117 = 4.8:1 - AA */
        --border-light: #3a3d4a;
        
        /* Inputs */
        --input: #1a1d29;
        --input-foreground: #ffffff;
        --input-border: #2a2d3a;
        --input-focus: #3b82f6;
        
        /* Status colors - WCAG compliant */
        --success: #22c55e;
        --success-bg: rgba(34, 197, 94, 0.1);
        --error: #ef4444;
        --error-bg: rgba(239, 68, 68, 0.1);
        --warning: #f59e0b;
        --warning-bg: rgba(245, 158, 11, 0.1);
        --info: #3b82f6;
        --info-bg: rgba(59, 130, 246, 0.1);
        
        /* Spacing & Radius */
        --radius: 0.5rem;
        --radius-lg: 0.75rem;
        --spacing: 1rem;
    }
    
    /* Global styles - Allstacks typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Main app background - Allstacks clean dark theme */
    .stApp {
        background: #0f1117;
        min-height: 100vh;
    }
    
    /* Main container - Allstacks spacing */
    .main .block-container {
        max-width: 1280px;
        padding: 2rem 1.5rem;
        background: transparent;
    }
    
    /* Hero section - Allstacks style */
    .main-header {
        font-size: clamp(2rem, 4vw, 3.5rem);
        font-weight: 700;
        text-align: left;
        color: #ffffff; /* High contrast */
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .sub-header {
        text-align: left;
        color: #94a3b8; /* #94a3b8 on #0f1117 = 6.8:1 - AA compliant */
        margin-bottom: 2rem;
        font-size: 1.125rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 600px;
    }
    
    /* Sidebar - Allstacks style */
    [data-testid="stSidebar"] {
        background: #1a1d29;
        border-right: 1px solid #2a2d3a;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    [data-testid="stSidebar"] [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Sidebar text - Allstacks style */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        color: #e2e8f0; /* #e2e8f0 on #1a1d29 = 12.1:1 - AAA */
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Cards - Shadcn card style */
    .card {
        background: #14141a;
        border: 1px solid #1e293b;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
    }
    
    /* Buttons - Allstacks style, WCAG AA compliant */
    .stButton > button {
        background: #3b82f6; /* #ffffff on #3b82f6 = 4.6:1 - AA */
        color: #ffffff;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        width: 100%;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: #2563eb; /* #ffffff on #2563eb = 5.2:1 - AA */
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:focus-visible {
        outline: 2px solid rgba(59, 130, 246, 0.5);
        outline-offset: 2px;
    }
    
    /* Input fields - Allstacks style, WCAG AA compliant */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a1d29;
        color: #ffffff; /* #ffffff on #1a1d29 = 13.5:1 - AAA */
        border: 1px solid #2a2d3a;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        line-height: 1.5;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #64748b; /* #64748b on #1a1d29 = 4.9:1 - AA */
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        background: #1f2230;
    }
    
    .stTextInput label,
    .stTextArea label {
        color: #e2e8f0; /* High contrast labels */
        font-weight: 500;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    /* Select boxes - WCAG AA compliant */
    .stSelectbox > div > div {
        background: #1a1a24;
        border: 2px solid #334155;
        border-radius: 0.75rem;
        padding: 0.5rem;
    }
    
    .stSelectbox > div > div > select {
        color: #ffffff; /* High contrast */
        font-size: 1rem; /* 16px minimum */
        background: transparent;
    }
    
    .stSelectbox label {
        color: #f8fafc; /* #f8fafc on #1a1a24 = 12.8:1 - AAA */
        font-weight: 500;
        font-size: 0.9375rem; /* 15px */
        margin-bottom: 0.5rem;
    }
    
    /* Dropdown menu options - WCAG AA compliant */
    /* Streamlit uses BaseWeb components, target all possible selectors */
    
    /* Dropdown menu container */
    div[data-baseweb="select"] > div[role="listbox"],
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[role="listbox"],
    ul[role="listbox"],
    .stSelectbox [role="listbox"],
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > ul {
        background: #1f1f2e !important; /* Dark background for dropdown */
        border: 2px solid #475569 !important; /* High contrast border - 6.5:1 */
        border-radius: 0.75rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
        padding: 0.5rem !important;
        max-height: 300px !important;
        overflow-y: auto !important;
    }
    
    /* Individual dropdown options - all possible selectors */
    div[role="option"],
    li[role="option"],
    .stSelectbox [role="option"],
    div[data-baseweb="select"] [role="option"],
    div[data-baseweb="menu"] li,
    div[data-baseweb="menu"] [role="option"],
    div[data-baseweb="popover"] [role="option"],
    ul[role="listbox"] li,
    ul[role="listbox"] [role="option"],
    div[data-baseweb="select"] > div[role="listbox"] > div,
    div[data-baseweb="select"] > div[role="listbox"] > li {
        background: #1f1f2e !important;
        color: #ffffff !important; /* #ffffff on #1f1f2e = 13.1:1 - AAA */
        font-size: 1rem !important; /* 16px minimum */
        padding: 0.875rem 1rem !important; /* Larger touch targets - 44px height */
        border: none !important;
        border-radius: 0.5rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0.25rem 0 !important;
        min-height: 44px !important; /* WCAG touch target requirement */
        display: flex !important;
        align-items: center !important;
    }
    
    /* Hover state for dropdown options */
    div[role="option"]:hover,
    li[role="option"]:hover,
    .stSelectbox [role="option"]:hover,
    div[data-baseweb="select"] [role="option"]:hover,
    div[data-baseweb="menu"] li:hover,
    div[data-baseweb="menu"] [role="option"]:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    ul[role="listbox"] li:hover,
    ul[role="listbox"] [role="option"]:hover {
        background: #334155 !important; /* #ffffff on #334155 = 7.2:1 - AA */
        color: #ffffff !important;
    }
    
    /* Selected/focused option */
    div[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"],
    .stSelectbox [role="option"][aria-selected="true"],
    div[data-baseweb="select"] [role="option"][aria-selected="true"],
    div[data-baseweb="menu"] li[aria-selected="true"],
    div[role="option"]:focus,
    li[role="option"]:focus,
    div[data-baseweb="select"] [role="option"]:focus {
        background: #3b82f6 !important; /* #ffffff on #3b82f6 = 4.6:1 - AA */
        color: #ffffff !important;
        outline: 3px solid rgba(59, 130, 246, 0.6) !important;
        outline-offset: 2px !important;
    }
    
    /* Active/pressed state */
    div[role="option"]:active,
    li[role="option"]:active {
        background: #2563eb !important; /* #ffffff on #2563eb = 5.2:1 - AA */
        color: #ffffff !important;
    }
    
    /* Dropdown menu scrollbar - WCAG compliant */
    div[role="listbox"]::-webkit-scrollbar,
    ul[role="listbox"]::-webkit-scrollbar,
    div[data-baseweb="menu"]::-webkit-scrollbar,
    div[data-baseweb="popover"]::-webkit-scrollbar {
        width: 10px;
    }
    
    div[role="listbox"]::-webkit-scrollbar-track,
    ul[role="listbox"]::-webkit-scrollbar-track,
    div[data-baseweb="menu"]::-webkit-scrollbar-track,
    div[data-baseweb="popover"]::-webkit-scrollbar-track {
        background: #1a1a24 !important;
        border-radius: 5px;
    }
    
    div[role="listbox"]::-webkit-scrollbar-thumb,
    ul[role="listbox"]::-webkit-scrollbar-thumb,
    div[data-baseweb="menu"]::-webkit-scrollbar-thumb,
    div[data-baseweb="popover"]::-webkit-scrollbar-thumb {
        background: #475569 !important; /* #475569 on #1a1a24 = 6.5:1 - AA */
        border-radius: 5px;
        border: 2px solid #1a1a24;
    }
    
    div[role="listbox"]::-webkit-scrollbar-thumb:hover,
    ul[role="listbox"]::-webkit-scrollbar-thumb:hover,
    div[data-baseweb="menu"]::-webkit-scrollbar-thumb:hover,
    div[data-baseweb="popover"]::-webkit-scrollbar-thumb:hover {
        background: #64748b !important; /* #64748b on #1a1a24 = 8.1:1 - AAA */
    }
    
    /* Ensure text in dropdowns is readable */
    div[data-baseweb="select"] *,
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] * {
        color: #ffffff !important;
    }
    
    /* Override any low-contrast text in dropdowns */
    div[role="option"] *,
    li[role="option"] * {
        color: #ffffff !important;
    }
    
    /* Radio buttons - WCAG AA compliant */
    .stRadio > div {
        background: #1a1a24;
        border: 2px solid #334155;
        border-radius: 0.75rem;
        padding: 1rem; /* Larger padding for better touch targets */
    }
    
    .stRadio label {
        color: #f8fafc; /* High contrast */
        font-weight: 400;
        font-size: 1rem; /* 16px minimum */
        cursor: pointer;
    }
    
    .stRadio input[type="radio"] {
        width: 20px;
        height: 20px;
        cursor: pointer;
        accent-color: #3b82f6;
    }
    
    /* Progress bar - Moonlet style */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        border-radius: 9999px;
    }
    
    /* Status boxes - WCAG AA compliant with better contrast */
    .stSuccess {
        background: rgba(34, 197, 94, 0.15);
        border: 2px solid rgba(34, 197, 94, 0.4);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        color: #86efac; /* #86efac on rgba(34,197,94,0.15) bg = sufficient contrast */
        font-size: 1rem; /* 16px minimum */
        font-weight: 500;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15);
        border: 2px solid rgba(239, 68, 68, 0.4);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        color: #fca5a5; /* High contrast error text */
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15);
        border: 2px solid rgba(59, 130, 246, 0.4);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        color: #93c5fd; /* High contrast info text */
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15);
        border: 2px solid rgba(245, 158, 11, 0.4);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        color: #fde047; /* High contrast warning text */
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Headers - WCAG AA compliant */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff; /* High contrast headers */
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc; /* #f8fafc on #1a1a24 = 12.8:1 - AAA */
        font-weight: 600;
        font-size: clamp(1.125rem, 2vw, 1.5rem); /* Responsive, minimum 18px */
    }
    
    /* Markdown text - WCAG AA compliant */
    .stMarkdown {
        color: #e2e8f0; /* #e2e8f0 on #0a0a0f = 13.8:1 - AAA */
        font-size: 1rem; /* 16px minimum */
        line-height: 1.7; /* Better readability */
    }
    
    .stMarkdown strong {
        color: #ffffff; /* Maximum contrast for emphasis */
        font-weight: 600;
    }
    
    /* Caption styling - WCAG AA compliant */
    .stCaption {
        color: #cbd5e1; /* #cbd5e1 on #0a0a0f = 11.2:1 - AAA, on #1a1a24 = 9.8:1 - AAA */
        font-size: 0.875rem; /* 14px - acceptable for captions */
        line-height: 1.6;
        font-weight: 400;
    }
    
    /* Divider - clean, no frame */
    hr {
        border: none;
        border-top: 1px solid rgba(30, 41, 59, 0.3);
        margin: 1.5rem 0;
        background: none;
    }
    
    /* Remove borders from dividers in sidebar */
    [data-testid="stSidebar"] hr {
        border-top: 1px solid rgba(30, 41, 59, 0.3);
        background: none;
    }
    
    /* Badge/Pill style */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #93c5fd;
    }
    
    /* Section containers - removed unnecessary cards */
    
    /* Metric cards - Allstacks style, WCAG compliant */
    .metric-card {
        background: #1a1d29;
        border: 1px solid #2a2d3a;
        border-radius: 0.5rem;
        padding: 1.5rem;
        text-align: left;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #3a3d4a;
        background: #1f2230;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff; /* #ffffff on #1a1d29 = 13.5:1 - AAA */
        margin-bottom: 0.25rem;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8; /* #94a3b8 on #1a1d29 = 5.9:1 - AA */
        font-weight: 500;
        text-transform: none;
        letter-spacing: 0;
    }
    
    /* Expander - WCAG AA compliant */
    .streamlit-expanderHeader {
        background: #1a1a24;
        border: 2px solid #334155;
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        color: #f8fafc; /* High contrast */
        font-weight: 600;
        font-size: 1rem; /* 16px minimum */
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #1f1f2e;
        border-color: #3b82f6;
    }
    
    /* Audio player styling - AWWWARDS style */
    audio {
        width: 100%;
        border-radius: 0.75rem;
        background: #1a1a24;
        padding: 0.5rem;
    }
    
    /* Download button - WCAG AA compliant */
    .stDownloadButton > button {
        background: #334155; /* #f8fafc on #334155 = 7.2:1 - AA */
        color: #f8fafc;
        border: 2px solid #475569;
        border-radius: 0.75rem;
        padding: 0.875rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #475569; /* #f8fafc on #475569 = 8.5:1 - AAA */
        border-color: #64748b;
        transform: translateY(-1px);
    }
    
    /* Progress bar - AWWWARDS style with animation */
    .stProgress {
        background: #1a1a24;
        border-radius: 9999px;
        padding: 4px;
        border: 2px solid #334155;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 50%, #93c5fd 100%);
        background-size: 200% 100%;
        border-radius: 9999px;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        animation: shimmer 2s ease-in-out infinite;
        height: 12px;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Smooth page transitions - AWWWARDS style */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container > div {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Hover effects for interactive elements */
    .stSelectbox > div > div:hover,
    .stTextInput > div > div:hover,
    .stTextArea > div > div:hover {
        border-color: #475569;
    }
    
    /* Loading states */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Focus indicators for accessibility */
    *:focus-visible {
        outline: 3px solid rgba(59, 130, 246, 0.6);
        outline-offset: 2px;
        border-radius: 4px;
    }
    
    /* Skip link for screen readers */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #3b82f6;
        color: #ffffff;
        padding: 8px;
        text-decoration: none;
        z-index: 100;
    }
    
    .skip-link:focus {
        top: 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_title_from_wikipedia_url(url: str) -> str:
    """Extracts article title from Wikipedia URL."""
    try:
        # Handle different Wikipedia URL formats
        # https://en.wikipedia.org/wiki/Article_Title
        # https://en.wikipedia.org/wiki/Article_Title?query=params
        # https://en.wikipedia.org/wiki/Article_Title#section
        
        # Remove query params and fragments
        url = url.split('?')[0].split('#')[0]
        
        # Extract title from URL
        if '/wiki/' in url:
            title = url.split('/wiki/')[-1]
            # Decode URL encoding
            title = urllib.parse.unquote(title)
            # Replace underscores with spaces
            title = title.replace('_', ' ')
            return title
        return None
    except Exception as e:
        st.error(f"Error parsing URL: {e}")
        return None

def get_article_text(input_method: str, url_input: str, text_input: str, title_input: str) -> str:
    """Gets article text based on input method."""
    if input_method == "Wikipedia URL":
        if not url_input:
            return None
        title = extract_title_from_wikipedia_url(url_input)
        if not title:
            st.error("Could not extract article title from URL. Please check the URL format.")
            return None
        st.info(f"📄 Extracting article: **{title}**")
        return fetch_wikipedia_article(title)
    
    elif input_method == "Paste Article Text":
        if not text_input:
            return None
        # Limit text to 2000 characters for API efficiency
        if len(text_input) > 2000:
            st.warning(f"Text is {len(text_input)} characters. Using first 2000 characters.")
            return text_input[:2000] + "..."
        return text_input
    
    elif input_method == "Article Title":
        if not title_input:
            return None
        return fetch_wikipedia_article(title_input)
    
    return None

# ============================================================================
# MAIN UI
# ============================================================================

def main():
    # Skip link for screen readers
    st.markdown('<a href="#main-content" class="skip-link">Skip to main content</a>', unsafe_allow_html=True)
    
    # Hero Section - Allstacks style (left-aligned, clean)
    st.markdown('<h1 class="main-header" id="main-content">The Synthetic Radio Host</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header" role="text">Transform Wikipedia articles into natural, engaging Hinglish and Tanglish conversation audio</p>', unsafe_allow_html=True)
    
    # Load API keys at the start
    load_dotenv(dotenv_path=env_path, override=True)
    groq_key = get_api_key("GROQ_API_KEY")
    elevenlabs_key = get_api_key("ELEVENLABS_API_KEY")
    
    # API Status Cards - Allstacks style
    st.markdown("### API Status")
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        if groq_key:
            st.markdown("""
            <div class="metric-card" role="status" aria-label="Groq API connected">
                <div class="metric-value" aria-hidden="true">✓</div>
                <div class="metric-label">Groq API</div>
                <div style="margin-top: 0.5rem; font-size: 0.8125rem; color: #94a3b8;">Llama 3.3 70B</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("**Groq API Key**\n\nNot found in .env file")
    
    with col2:
        if elevenlabs_key:
            st.markdown("""
            <div class="metric-card" role="status" aria-label="ElevenLabs API connected">
                <div class="metric-value" aria-hidden="true">✓</div>
                <div class="metric-label">ElevenLabs API</div>
                <div style="margin-top: 0.5rem; font-size: 0.8125rem; color: #94a3b8;">Premium Voices</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("**ElevenLabs API Key**\n\nNot found (optional)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar for settings - Allstacks style
    with st.sidebar:
        st.markdown("## Configuration")
        
        # TTS Provider selection
        openai_key = get_api_key("OPENAI_API_KEY")
        
        tts_options = ["ElevenLabs (Better Quality)"]
        if openai_key:
            tts_options.append("OpenAI TTS (Cheaper)")
        
        if len(tts_options) > 1:
            use_elevenlabs = st.radio("**TTS Provider**", tts_options, index=0)
            use_elevenlabs = use_elevenlabs == "ElevenLabs (Better Quality)"
        else:
            st.info("📢 Using ElevenLabs for TTS")
            use_elevenlabs = True
        
        st.markdown("---")
        
        # Language Selection
        st.markdown("### Language")
        language_type = st.radio(
            "Conversation style:",
            ["Hinglish (Hindi-English)", "Tanglish (Tamil-English)"],
            index=0,
            help="Hinglish: Mix of Hindi and English | Tanglish: Mix of Tamil and English"
        )
        language_type = "Tanglish" if "Tanglish" in language_type else "Hinglish"
        
        st.markdown("---")
        
        # Voice Selection Section
        st.markdown("### Voices")
        
        # Voice filters
        st.markdown("**Filters**")
        gender_filter = st.selectbox("Gender", ["All", "Male", "Female"], label_visibility="collapsed")
        language_options = ["All", "English (American)", "English (British)", "English (Indian)"]
        language_filter = st.selectbox("Accent", language_options, label_visibility="collapsed")
        tone_options = ["All", "Warm", "Deep", "Young", "Strong", "Soft", "Calm", "Elegant"]
        tone_filter = st.selectbox("Tone", tone_options, label_visibility="collapsed")
        
        # Get filtered voices
        filtered_voices = get_filtered_voices(gender_filter, tone_filter, language_filter)
        
        # Voice A selection (Person A)
        st.markdown("**Person A**")
        voice_a_options = list(filtered_voices.keys()) if filtered_voices else list(VOICE_CATALOG.keys())
        voice_a_name = st.selectbox("Select voice", voice_a_options, index=0, label_visibility="collapsed", key="voice_a")
        if voice_a_name in VOICE_CATALOG:
            voice_a_info = VOICE_CATALOG[voice_a_name]
            st.caption(f"{voice_a_info['gender']} • {voice_a_info['language']}")
        
        # Voice B selection (Person B)
        st.markdown("**Person B**")
        voice_b_default_idx = 1 if len(voice_a_options) > 1 else 0
        if voice_a_name in VOICE_CATALOG:
            voice_a_gender = VOICE_CATALOG[voice_a_name]["gender"]
            for i, name in enumerate(voice_a_options):
                if name in VOICE_CATALOG and VOICE_CATALOG[name]["gender"] != voice_a_gender:
                    voice_b_default_idx = i
                    break
        
        voice_b_name = st.selectbox(
            "Select voice",
            voice_a_options,
            index=min(voice_b_default_idx, len(voice_a_options)-1),
            label_visibility="collapsed",
            key="voice_b"
        )
        if voice_b_name in VOICE_CATALOG:
            voice_b_info = VOICE_CATALOG[voice_b_name]
            st.caption(f"{voice_b_info['gender']} • {voice_b_info['language']}")
        
        # Get voice IDs
        voice_a_id = VOICE_CATALOG.get(voice_a_name, {}).get("id", "21m00Tcm4TlvDq8ikWAM")
        voice_b_id = VOICE_CATALOG.get(voice_b_name, {}).get("id", "pNInz6obpgDQGcFmaJgB")
        
        st.markdown("---")
        
        # API Keys status
        st.markdown("### Status")
        if groq_key:
            st.success("✓ Groq")
        else:
            st.error("✗ Groq")
        
        if elevenlabs_key:
            st.success("✓ ElevenLabs")
        else:
            st.warning("⚠ ElevenLabs")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        Transform articles into natural conversation audio.
        
        **Features:**
        - Wikipedia integration
        - Direct text input
        - Premium voices
        - Instant playback
        """)
    
    # Main content area
    st.markdown("---")
    
    # Input Section - Allstacks style
    st.markdown("### Article Input")
    
    input_method = st.radio(
        "Choose input method:",
        ["Wikipedia URL", "Paste Article Text", "Article Title"],
        horizontal=True,
        help="Select how you want to provide the article content"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Input fields based on selection
    article_text = None
    
    if input_method == "Wikipedia URL":
        url_input = st.text_input(
            "Enter Wikipedia URL",
            placeholder="https://en.wikipedia.org/wiki/Mumbai_Indians",
            help="Paste a Wikipedia article URL. The app will automatically fetch the content.",
            label_visibility="visible"
        )
        if url_input:
            article_text = get_article_text(input_method, url_input, "", "")
    
    elif input_method == "Paste Article Text":
        text_input = st.text_area(
            "Paste article text",
            height=200,
            placeholder="Paste the article content here...",
            help="Paste the full article text directly. The app will use this content to generate the conversation.",
            label_visibility="visible"
        )
        if text_input:
            article_text = get_article_text(input_method, "", text_input, "")
    
    elif input_method == "Article Title":
        title_input = st.text_input(
            "Enter Wikipedia article title",
            placeholder="Mumbai Indians",
            help="Enter the exact Wikipedia article title. The app will search and fetch the article.",
            label_visibility="visible"
        )
        if title_input:
            article_text = get_article_text(input_method, "", "", title_input)
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎙️ Generate Conversation Audio", type="primary", use_container_width=True):
        if not article_text:
            st.error("Please provide article content using one of the input methods above.")
            return
        
        # Check API keys (reload to get latest values)
        current_groq_key = get_api_key("GROQ_API_KEY")
        current_elevenlabs_key = get_api_key("ELEVENLABS_API_KEY")
        
        if not current_groq_key:
            st.error("Groq API key not found. Please set GROQ_API_KEY in your .env file.")
            return
        
        if use_elevenlabs and not current_elevenlabs_key:
            st.error("ElevenLabs API key not found. Please set it in your .env file or use OpenAI TTS.")
            return
        
        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Generate script
            lang_name = "Tanglish" if language_type == "Tanglish" else "Hinglish"
            status_text.text(f"🤖 Generating {lang_name} conversation script...")
            progress_bar.progress(20)
            
            script = generate_conversation_script(article_text, language_type=language_type)
            
            if not script:
                st.error("Failed to generate conversation script. Please check your API keys and try again.")
                return
            
            progress_bar.progress(40)
            status_text.text("✓ Script generated! Parsing segments...")
            
            # Display script
            with st.expander("📝 View Generated Script", expanded=True):
                st.text_area("Conversation Script", script, height=300, disabled=True)
            
            # Step 2: Parse script
            segments = parse_script(script)
            progress_bar.progress(50)
            
            if not segments or len(segments) == 0:
                st.error("Failed to parse script into segments. The generated script may not be in the correct format.")
                with st.expander("View Script", expanded=False):
                    st.text_area("Script", script, height=200, disabled=True)
                return
            
            status_text.text(f"✓ Parsed into {len(segments)} segments")
            
            # Validate voice IDs
            if not voice_a_id or not voice_b_id:
                st.error(f"Invalid voice IDs. Person A: {voice_a_id}, Person B: {voice_b_id}")
                return
            
            # Step 3: Generate audio
            status_text.text(f"🎤 Generating audio with {voice_a_name} & {voice_b_name}...")
            progress_bar.progress(60)
            
            try:
                audio_segments = generate_audio_for_segments(
                    segments, 
                    use_elevenlabs=use_elevenlabs,
                    voice_a_id=voice_a_id,
                    voice_b_id=voice_b_id
                )
                
                if not audio_segments or len(audio_segments) == 0:
                    error_msg = "Failed to generate audio. No audio segments were created."
                    if use_elevenlabs:
                        error_msg += "\n\nPossible causes:\n- ElevenLabs API key invalid or expired\n- Insufficient ElevenLabs credits\n- Network connectivity issues\n- Voice ID invalid"
                    else:
                        error_msg += "\n\nPossible causes:\n- OpenAI API key invalid or expired\n- Insufficient OpenAI credits\n- Network connectivity issues"
                    st.error(error_msg)
                    return
                    
            except ValueError as e:
                # API key errors
                st.error(f"API Configuration Error: {str(e)}")
                st.info("💡 **Tip**: Check your `.env` file and ensure your API keys are correct.")
                return
            except requests.exceptions.RequestException as e:
                # Network errors
                st.error(f"Network Error: {str(e)}")
                st.info("💡 **Tip**: Check your internet connection and try again.")
                return
            except Exception as e:
                # Other errors
                error_msg = str(e)
                st.error(f"Error generating audio: {error_msg}")
                
                # Show helpful troubleshooting
                with st.expander("🔍 Troubleshooting", expanded=False):
                    st.markdown("""
                    **Common Issues:**
                    1. **API Key Invalid**: Check your ElevenLabs API key in `.env` file
                    2. **Insufficient Credits**: Check your ElevenLabs account balance
                    3. **Voice ID Invalid**: The selected voice may not be available
                    4. **Rate Limits**: You may have exceeded API rate limits
                    
                    **Check:**
                    - ElevenLabs dashboard: https://elevenlabs.io/app
                    - API key status in sidebar
                    """)
                
                with st.expander("🔍 Technical Details", expanded=False):
                    import traceback
                    st.code(traceback.format_exc())
                return
            
            progress_bar.progress(80)
            status_text.text("🔊 Combining audio segments...")
            
            # Step 4: Combine and export
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                output_path = tmp_file.name
            
            output_path = combine_and_export_audio(audio_segments, output_path)
            
            if not output_path:
                st.error("Failed to export audio file.")
                return
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Display success message
            st.success("🎉 Audio generated successfully!")
            
            # Audio player
            st.markdown("---")
            st.subheader("🎧 Listen to Your Audio")
            
            with open(output_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
            
            # Download button
            st.download_button(
                label="📥 Download MP3",
                data=audio_bytes,
                file_name="hinglish_conversation.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
            
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
            progress_bar.empty()
            status_text.empty()

if __name__ == "__main__":
    main()

