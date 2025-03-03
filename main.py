import streamlit as st
import os
import hashlib
from gtts import gTTS
from io import BytesIO
import base64
import time
import tempfile
import requests

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

# Hide Streamlit elements and make static
st.markdown("""
    <style>
        /* Hide Streamlit elements */
        footer {display: none !important;}
        #MainMenu {display: none !important;}
        header {display: none !important;}
        .stDeployButton {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        .viewerBadge_link__1QSob {display: none !important;}
        button[title="View fullscreen"] {display: none !important;}
        
        /* Make app static */
        .stApp {
            height: 100vh !important;
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
        }
        
        .main .block-container {
            height: 100vh !important;
            overflow: hidden !important;
            padding: 1rem !important;
        }
        
        /* Main container */
        .main-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 10px !important;
            height: calc(100vh - 2rem) !important;
            overflow: hidden !important;
            position: fixed !important;
            width: calc(100% - 2rem) !important;
        }
        
        /* Image sizing */
        .element-container img {
            max-height: 35vh !important;
            width: auto !important;
            object-fit: contain !important;
            margin: 0 auto !important;
        }
        
        /* Content spacing */
        .character {
            font-size: 42px !important;
            font-weight: bold !important;
            margin: 5px 0 !important;
            text-align: center !important;
        }
        
        .pinyin {
            font-size: 20px !important;
            color: #666 !important;
            margin: 5px 0 !important;
            text-align: center !important;
        }
        
        .explanation {
            font-size: 18px !important;
            font-weight: 500 !important;
            margin: 5px 0 10px 0 !important;
            text-align: center !important;
            padding: 0 15px !important;
        }
        
        /* Audio player */
        div.stAudio {
            display: flex !important;
            justify-content: center !important;
            margin: 5px auto !important;
        }
        
        div.stAudio > audio {
            width: 100px !important;
            height: 35px !important;
        }
        
        /* Button styling */
        .stButton {
            display: flex !important;
            justify-content: center !important;
            margin: 10px auto !important;
        }
        
        .stButton button {
            width: 120px !important;
        }
        
        /* Prevent scrolling */
        body {
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
            height: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# At the top of the file, add more detailed error handling
try:
    from gtts import gTTS
    AUDIO_ENABLED = True
except ImportError as e:
    AUDIO_ENABLED = False
    st.error(f"Detailed error: {str(e)}")
    st.warning("Audio functionality is not available. Installing required packages...")
    try:
        import subprocess
        subprocess.check_call(["pip", "install", "gTTS==2.5.0", "click>=7.0"])
        from gtts import gTTS
        AUDIO_ENABLED = True
        st.success("Successfully installed audio packages!")
    except Exception as e:
        st.error(f"Failed to install packages: {str(e)}")

# CSS styles
st.markdown("""
    <style>
.stApp {
    background-color: white !important;
    padding: 5px 10px !important;
    color: black !important;
}

.character {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
    text-align: center;
    color: black !important;
}

.pinyin {
    font-size: 18px;
    color: #666;
    margin: 5px 0;
    text-align: center;
}

.explanation {
    font-size: 16px;
    margin: 10px 0;
    text-align: center;
    text-transform: uppercase;
    font-weight: bold;
    color: black !important;
}

/* Button styling */
.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}

.stButton > button {
    background-color: white !important;
    color: black !important;
    border: 2px solid black !important;
    border-radius: 5px !important;
    padding: 5px 15px !important;
    font-weight: 500 !important;
    margin: 0 auto !important;
}

.stButton > button:hover {
    background-color: #f0f0f0 !important;
    border-color: black !important;
        }
        
        /* Audio player styling */
.stAudio {
    width: 50% !important;
    margin: 5px auto !important;
    display: flex !important;
    justify-content: center !important;
}

.stAudio > audio {
    width: 90px !important;
    height: 30px !important;
}

audio::-webkit-media-controls-panel {
    background-color: #666666 !important;  /* Darker grey */
}

audio::-webkit-media-controls-play-button {
    transform: scale(1.2) !important;
    margin: 0 8px !important;
    color: white !important;
}

audio::-webkit-media-controls-current-time-display,
audio::-webkit-media-controls-time-remaining-display {
    color: white !important;
    font-size: 12px !important;
}

/* Center column content */
[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
}

/* Mobile optimization */
.main-container {
    max-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10px;
}

/* Adjust image container */
.image-container {
    flex: 0 0 auto;
    margin-bottom: 10px;
}

/* Text content */
.text-content {
    flex: 0 0 auto;
    margin: 10px 0;
}

/* Button container */
.button-container {
    flex: 0 0 auto;
    margin-top: 10px;
}

/* Audio container styling */
.audio-container {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
            width: 100% !important;
    margin: 15px auto !important;
}

.audio-container audio {
    width: 35px !important;
    height: 35px !important;
    border-radius: 50% !important;
    background-color: #666666 !important;
}

/* Hide audio controls except play button */
.audio-container audio::-webkit-media-controls-panel {
    background-color: #666666 !important;
    display: flex !important;
    justify-content: center !important;
}

.audio-container audio::-webkit-media-controls-play-button {
    transform: scale(1.2) !important;
            margin: 0 !important;
        }
        
.audio-container audio::-webkit-media-controls-timeline,
.audio-container audio::-webkit-media-controls-current-time-display,
.audio-container audio::-webkit-media-controls-time-remaining-display,
.audio-container audio::-webkit-media-controls-volume-slider,
.audio-container audio::-webkit-media-controls-mute-button {
    display: none !important;
}

/* Center all content */
.main-container {
    max-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px !important;
    text-align: center !important;
}

.text-content {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    margin: 10px 0 !important;
}

.character, .pinyin, .explanation {
    width: 100% !important;
    text-align: center !important;
}

.image-container {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    margin-bottom: 15px !important;
}

.button-container {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    margin-top: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

def get_audio(text):
    """Simple audio generation"""
    try:
        # Special cases for pronunciation
        special_cases = {
            "HHHH": "哈哈哈哈",
            "666": "六六六",
            "88": "八八",
            "3Q": "三Q",
            "WC": "哇草",
            "SB": "傻逼",
            "6": "六",
            "city不city": "city 不 city"
        }
        
        # English words to pronounce as-is
        english_words = ["Vlog", "Flag", "Crush", "Emo"]
        
        # Generate audio
        if text in english_words:
            tts = gTTS(text=text, lang='en', slow=False)
        elif text in special_cases:
            tts = gTTS(text=special_cases[text], lang='zh-cn', slow=False)
        else:
            tts = gTTS(text=text, lang='zh-cn', slow=False)
            
        # Save to BytesIO
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.read()
    except:
        return None

def get_audio_url(text):
    """Get audio URL from Google Drive"""
    try:
        # Map Chinese text to Google Drive URLs
        audio_urls = {
            "吃瓜群众": "1kHPyyhXI9NfcFqy4wttQA8mt1_LHf53F",
            "打卡": "19-Rf6UgMoThUD69Ss8-jYCiqaHhLZNJq",
            "真香": "1JS7JuGR-eu9VPzIA5GRDMDutZtEbV29g",
            "猛男必看": "1jp2KnpVxEkzLJ3c3YlKBhtHiPdvpQqI7",
            "好家伙": "1c0Pu0FWtfu6FLhJJKESIPRrRh_5D-sDT",
            "安排上了": "1TQtdLpJQ3CG98h6ru1__KweAktch5-Ns",
            "yyds": "10u6_GwJGUEkt9dSQes-3KB3CecfBeODy",
            "爷青回": "1GTdUJ9QwVEz0FVpTCrHf7VvBbanktBRt",
            "社死": "1sWx_APNyBwE7mL6maui06teFpmOv609S",
            "躺平": "1if-B4-wc1YC6QQRtyo3JUqA6IOI3cRY9",
            "凡尔赛文学": "10kS2ykJlLmSnvLu4PfspRaJ0_VB44-_q",
            "加油": "1It7KYsXZFsfKZ0EEYn_kOQFPLRSe9e4M",
            "厉害": "1BztTgQijkc3cMIFI8No-pFV3jYs-dZBp",
            "梗": "1uGrjOyrhpy83Oqk-f2bUqzCcC5Kc2BPj",
            "下头": "1-aKxFaxOVQYzy5q8QOVwIucPfbC3yHyp",
            "离谱": "1SgjTQX_YOqh_5P9Te1dB8lTomOOcQ_BW",
            "三连": "1DiwhRHGfQsVJPaGnVCZQlENHds-rPSHe",
            "太难了": "1Fke8YLmNYSpDDyPiQKqJ5xBjEFF4g362",
            "内卷": "1oc3YQRiQijbUTf3umM2ufyJAVgwYrAGV",
            "整活": "1OJmzDSRVwgihcspJbwTOqbdQLI4Smuf3",
            "都可以": "1b9-kOGMGf6JtYQNbM8nbFYYEAeEC9LEv",
            "有点东西": "1v9NEYEZo7F8x-8RZXYue3GKe7MQpwgdF",
            "妈呀": "1kmcaHmP5Lw4bVw9ijFqeEoMyZsqqb6ec",
            "卧槽": "1NbuisXVsoBUNlkvTH9kkjMT_JOAR4mdk",
            "我可以": "1FN7eEQS7IjL7pLE1cheQc8FBC7cBsxev",
            "摆烂": "1xNxu1-P3eGfAVlDAW243pgdrEMjnBX8x",
            "拿捏": "1NhtHt1waMmnD1sxgyP6icUXcLjyUB-R2",
            "盘它": "1TmBOK4EeLrVoM1zeq1U0TUuMCUzjSjmZ",
            "搞钱": "1ZzZAFqz3Vymss6HQhW82ERrV0Nt16ZBi",
            "丢人": "1Vkm4Hk8Bu8ycglqPrtEqFPZM9BF1Hy_v"
        }
        
        if text in audio_urls:
            file_id = audio_urls[text]
            url = f"https://drive.google.com/uc?id={file_id}&export=download"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                return BytesIO(response.content)
        return None
    except:
        return None

# Flashcard data
flashcards = [
    {
        "chinese": "吃瓜群众",
        "pinyin": "chī guā qún zhòng",
        "english": "Melon-eating crowd, onlookers",
        "meme_url": "https://imgur.com/c9eCIJJ.png"
    },
    {
        "chinese": "打卡",
        "pinyin": "dǎ kǎ",
        "english": "Clock in, post about it",
        "meme_url": "https://i.imgur.com/O99K0qq.png"
    },
    {
        "chinese": "真香",
        "pinyin": "zhēn xiāng",
        "english": "Smells good, used for admitting something is good",
        "meme_url": "https://i.imgur.com/CPgv2ef.png"
    },
    {
        "chinese": "猛男必看",
        "pinyin": "měng nán bì kàn",
        "english": "Must-see for macho men (ironic)",
        "meme_url": "https://i.imgur.com/AYAyPGy.png"
    },
    {
        "chinese": "好家伙",
        "pinyin": "hǎo jiā huǒ",
        "english": "Wow, surprising (sarcastic)",
        "meme_url": "https://i.imgur.com/7I0OdQV.png"
    },
    {
        "chinese": "安排上了",
        "pinyin": "ān pái shàng le",
        "english": "It's been arranged, all set",
        "meme_url": "https://i.imgur.com/ePmcVtm.png"
    },
    {
        "chinese": "yyds",
        "pinyin": "yǒng yuǎn de shén",
        "english": "Forever the GOAT",
        "meme_url": "https://i.imgur.com/PtQGQ77.png"
    },
    {
        "chinese": "爷青回",
        "pinyin": "yé qīng huí",
        "english": "Grandpa feels young again (nostalgia)",
        "meme_url": "https://i.imgur.com/ldgX6iJ.png"
    },
    {
        "chinese": "社死",
        "pinyin": "shè sǐ",
        "english": "Social death, embarrassment",
        "meme_url": "https://i.imgur.com/HyEyGus.png"
    },
    {
        "chinese": "躺平",
        "pinyin": "tǎng píng",
        "english": "Lie flat, give up resisting pressure",
        "meme_url": "https://i.imgur.com/k5o58WP.png"
    },
    {
        "chinese": "凡尔赛文学",
        "pinyin": "fán ěr sài wén xué",
        "english": "Versailles literature, humblebragging",
        "meme_url": "https://i.imgur.com/ypwI2Sb.png"
    },
    {
        "chinese": "加油",
        "pinyin": "jiā yóu",
        "english": "Keep it up, encouragement",
        "meme_url": "https://i.imgur.com/9gNSaV8.png"
    },
    {
        "chinese": "厉害",
        "pinyin": "lì hài",
        "english": "Awesome, great",
        "meme_url": "https://i.imgur.com/ZC7RZf9.png"
    },
    {
        "chinese": "梗",
        "pinyin": "gěng",
        "english": "Meme, joke",
        "meme_url": "https://i.imgur.com/QV7cshk.png"
    },
    {
        "chinese": "下头",
        "pinyin": "xià tóu",
        "english": "Disappointing, boring",
        "meme_url": "https://i.imgur.com/dtnTtoN.png"
    },
    {
        "chinese": "离谱",
        "pinyin": "lí pǔ",
        "english": "Ridiculous",
        "meme_url": "https://i.imgur.com/CYr1YWZ.png"
    },
    {
        "chinese": "三连",
        "pinyin": "sān lián",
        "english": "Three consecutive actions, triple support",
        "meme_url": "https://i.imgur.com/DDgHMJF.png"
    },
    {
        "chinese": "太难了",
        "pinyin": "tài nán le",
        "english": "Too difficult, exaggerated struggle",
        "meme_url": "https://i.imgur.com/CpZRcx1.png"
    },
    {
        "chinese": "内卷",
        "pinyin": "nèi juǎn",
        "english": "Involution, pointless competition",
        "meme_url": "https://i.imgur.com/lQoZRtk.png"
    },
    {
        "chinese": "整活",
        "pinyin": "zhěng huó",
        "english": "Making a splash, being creative",
        "meme_url": "https://i.imgur.com/s8K37GP.png"
    },
    {
        "chinese": "都可以",
        "pinyin": "dōu kě yǐ",
        "english": "Whatever, anything works",
        "meme_url": "https://i.imgur.com/UzdGndv.png"
    },
    {
        "chinese": "有点东西",
        "pinyin": "yǒu diǎn dōng xi",
        "english": "This is good, something valuable",
        "meme_url": "https://i.imgur.com/mAXsYa7.png"
    },
    {
        "chinese": "妈呀",
        "pinyin": "mā ya",
        "english": "Oh my gosh!",
        "meme_url": "https://i.imgur.com/juZ9hn2.png"
    },
    {
        "chinese": "卧槽",
        "pinyin": "wò cào",
        "english": "WTF!",
        "meme_url": "https://i.imgur.com/c5OPemG.png"
    },
    {
        "chinese": "我可以",
        "pinyin": "wǒ kě yǐ",
        "english": "I can do it (humorous exaggeration)",
        "meme_url": "https://i.imgur.com/ySriP84.png"
    },
    {
        "chinese": "摆烂",
        "pinyin": "bǎi làn",
        "english": "Slack off, stop trying",
        "meme_url": "https://i.imgur.com/k4IHGBI.png"
    },
    {
        "chinese": "拿捏",
        "pinyin": "ná niē",
        "english": "Master something, handle it perfectly",
        "meme_url": "https://i.imgur.com/AiVqZhn.png"
    },
    {
        "chinese": "盘它",
        "pinyin": "pán tā",
        "english": "Go for it, take control",
        "meme_url": "https://i.imgur.com/2i5ybdE.png"
    },
    {
        "chinese": "搞钱",
        "pinyin": "gǎo qián",
        "english": "Make money",
        "meme_url": "https://i.imgur.com/gWIrpQR.png"
    },
    {
        "chinese": "丢人",
        "pinyin": "diū rén",
        "english": "Embarrassing, shameful",
        "meme_url": "https://i.imgur.com/mBWjc9O.png"
    }
]

def main():
    # Initialize session state
    if 'index' not in st.session_state:
        st.session_state.index = 0

    # Create a container with fixed height for mobile optimization
    with st.container():
        # Get current flashcard
        current_card = flashcards[st.session_state.index]
        
        # Main container
        st.markdown("""
            <div class="main-container">
        """, unsafe_allow_html=True)
        
        # Image with centering
        col1, col2, col3 = st.columns([1,6,1])
        with col2:
            st.image(current_card['meme_url'], use_column_width=False)
        
        # Chinese character
        st.markdown(f"""
            <div class="character">{current_card['chinese']}</div>
        """, unsafe_allow_html=True)
        
        # Pinyin
        st.markdown(f"""
            <div class="pinyin">{current_card['pinyin']}</div>
        """, unsafe_allow_html=True)
        
        # Audio below pinyin
        audio_bytes = get_audio_url(current_card["chinese"])
        if audio_bytes:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.audio(audio_bytes, format='audio/mp3')
        
        # English definition
        st.markdown(f"""
            <div class="explanation">{current_card['english']}</div>
        """, unsafe_allow_html=True)
        
        # Next button below definition
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.rerun()
        
        # Close main container
        st.markdown("</div>", unsafe_allow_html=True)

    # Add this at the start of main()
    st.markdown("""
        <script>
            // Prevent scrolling
            document.body.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.addEventListener('touchmove', function(e) {
                e.preventDefault();
            }, { passive: false });
        </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
