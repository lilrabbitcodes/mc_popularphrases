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
        
        /* Base styles */
        body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
            height: 100% !important;
        }
        
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
        }
        
        .main .block-container {
            margin: 0 !important;
            padding: 0 !important;
            max-width: none !important;
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        /* Flashcard container */
        .flashcard-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: flex-start !important;
            padding: 0.5rem !important;
            margin: 0 auto !important;
            max-width: 600px !important;
            width: 100% !important;
            height: 100vh !important;
            box-sizing: border-box !important;
            gap: 0.3rem !important;
        }
        
        /* Image container */
        .image-container {
            width: 100% !important;
            height: 30vh !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .image-container img {
            max-height: 100% !important;
            width: auto !important;
            object-fit: contain !important;
        }
        
        /* Content wrapper */
        .content-wrapper {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
            padding: 0 !important;
            gap: 0.3rem !important;
            margin-top: -0.5rem !important;
        }
        
        /* Text container */
        .text-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
            gap: 0.3rem !important;
        }
        
        /* Text styles */
        .chinese-text {
            font-size: 2rem !important;
            font-weight: bold !important;
            margin: 0 !important;
            text-align: center !important;
            width: 100% !important;
            line-height: 1.2 !important;
        }
        
        .pinyin-text {
            font-size: 1.2rem !important;
            color: #666 !important;
            margin: 0 !important;
            text-align: center !important;
            width: 100% !important;
            line-height: 1.2 !important;
        }
        
        .english-text {
            font-size: 1rem !important;
            margin: 0 !important;
            text-align: center !important;
            width: 100% !important;
            line-height: 1.2 !important;
            color: #333 !important;
        }
        
        /* Audio styles */
        .stAudio {
            display: flex !important;
            justify-content: center !important;
            margin: 0.2rem auto !important;
            width: 80% !important;
            max-width: 300px !important;
        }
        
        .stAudio > audio {
            width: 100% !important;
            height: 32px !important;
            border-radius: 16px !important;
        }
        
        /* Button styles */
        .stButton {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }
        
        .stButton > button {
            padding: 0.5rem 1.5rem !important;
            font-size: 1rem !important;
            border-radius: 20px !important;
            background-color: #f0f2f6 !important;
            border: none !important;
            width: auto !important;
            min-width: 120px !important;
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

def get_audio_path(text, lang='zh-cn'):
    """Generate audio file path based on text hash"""
    # Create audio directory if it doesn't exist
    os.makedirs('audio_cache', exist_ok=True)
    
    # Generate unique filename based on text and language
    filename = hashlib.md5(f"{text}_{lang}".encode()).hexdigest() + ".mp3"
    return os.path.join('audio_cache', filename)

def generate_audio(text, lang='zh-cn'):
    """Generate audio file for given text if it doesn't exist"""
    audio_path = get_audio_path(text, lang)
    
    # Generate audio file if it doesn't exist
    if not os.path.exists(audio_path):
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_path)
    
    return audio_path

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
            session = requests.Session()
            response = session.get(url, stream=True)
            
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    token = value
                    url = f"{url}&confirm={token}"
                    response = session.get(url, stream=True)
                    break
            
            if response.status_code == 200:
                return BytesIO(response.content)
            
        # Fallback to gTTS
        audio_path = generate_audio(text)
        with open(audio_path, 'rb') as f:
            return BytesIO(f.read())
                
    except Exception as e:
        print(f"Error getting audio: {str(e)}")
        try:
            audio_path = generate_audio(text)
            with open(audio_path, 'rb') as f:
                return BytesIO(f.read())
        except Exception as e:
            print(f"Failed to generate fallback audio: {str(e)}")
            return None
    
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
    
    # Get current flashcard
    current_card = flashcards[st.session_state.index]
    
    # Create container for flashcard
    container = st.container()
    
    with container:
        # Image
        st.image(current_card['meme_url'], use_column_width=True)
        
        # Chinese text
        st.markdown(f"### {current_card['chinese']}")
        
        # Pinyin
        st.markdown(f"*{current_card['pinyin']}*")
        
        # Audio
        try:
            audio_bytes = get_audio_url(current_card["chinese"])
            if audio_bytes:
                st.audio(audio_bytes, format='audio/mp3')
        except Exception as e:
            st.error("Audio not available")
        
        # English definition
        st.markdown(f"**{current_card['english']}**")
        
        # Next button
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.rerun()

if __name__ == "__main__":
    main()
