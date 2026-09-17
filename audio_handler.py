import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

# Global variable to track and kill the current audio playback process
current_playback = None

def speak(text, speed_factor=1.12):
    """Converts text to speech, speeds it up smoothly, and plays it via simpleaudio."""
    global current_playback
    if not text.strip():
        return

    temp_file = "temp_speech.mp3"
    speed_file = "speed_speech.mp3"
    
    try:
        # 1. Generate the smooth Google TTS audio
        tts = gTTS(text=text, lang='en')
        tts.save(temp_file)
        
        # 2. Load audio with pydub
        audio = AudioSegment.from_mp3(temp_file)
        
        # 3. Speed up playback while correcting the high pitch effect
        new_sample_rate = int(audio.frame_rate * speed_factor)
        faster_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        
        # This line forces the frequency back down to normal so it doesn't sound like a kid
        faster_audio = faster_audio.set_frame_rate(audio.frame_rate)
        
        faster_audio.export(speed_file, format="mp3")
        
        # 4. Play asynchronously
        playable_segment = AudioSegment.from_mp3(speed_file)
        current_playback = _play_with_simpleaudio(playable_segment)
        current_playback.wait_done() 
        
    except Exception as e:
        print(f"Audio playback error: {e}")
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)
        if os.path.exists(speed_file): os.remove(speed_file)

def stop_audio():
    """Instantly kills any active audio playback."""
    global current_playback
    if current_playback and current_playback.is_playing():
        current_playback.stop()
