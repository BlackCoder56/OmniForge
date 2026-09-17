import os
import time
import pygame
from gtts import gTTS
from pydub import AudioSegment

def speak(text, speed_factor=1.12):
    """Converts text to speech, speeds it up smoothly, and plays it safely via Pygame."""
    if not text.strip():
        return

    temp_file = "temp_speech.mp3"
    speed_file = "speed_speech.mp3"
    
    try:
        # 1. Generate smooth Google TTS audio
        tts = gTTS(text=text, lang='en')
        tts.save(temp_file)
        
        # 2. Adjust speed natively using pydub
        audio = AudioSegment.from_mp3(temp_file)
        new_sample_rate = int(audio.frame_rate * speed_factor)
        faster_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        faster_audio = faster_audio.set_frame_rate(audio.frame_rate)
        faster_audio.export(speed_file, format="mp3")
        
        # 3. Initialize Pygame Mixer safely
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # 4. Load and play the audio file
        pygame.mixer.music.load(speed_file)
        pygame.mixer.music.play()
        
        # 5. Block the thread until audio completes playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
            
        # Unload the file from memory so it can be safely deleted on the next line
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"Audio playback error: {e}")
    finally:
        # Secure file clean-up loops
        try:
            if os.path.exists(temp_file): os.remove(temp_file)
            if os.path.exists(speed_file): os.remove(speed_file)
        except:
            pass

def stop_audio():
    """Instantly kills any active audio playback channel."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
