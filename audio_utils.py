from gtts import gTTS
import os
import hashlib

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