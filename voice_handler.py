import os
import sys
import speech_recognition as sr

def suppress_alsa_errors():
    """Redirects standard error to hide annoying ALSA/JACK logs."""
    sys.stderr.flush()
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr

def restore_stderr(old_stderr):
    """Restores standard error logs back to normal."""
    sys.stderr.flush()
    os.dup2(old_stderr, 2)
    os.close(old_stderr)

def record_active_mic(timeout=15):
    """Listens to the mic immediately and returns the captured audio object."""
    old_err = suppress_alsa_errors()
    recognizer = sr.Recognizer()
    
    # Fast adjustments for human dialogue window
    recognizer.pause_threshold = 1.0
    recognizer.non_speaking_duration = 0.3
    
    try:
        with sr.Microphone() as source:
            restore_stderr(old_err)
            print("[System: Microphone Open]")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
            return audio
    except Exception as e:
        print(f"Mic tracking failure: {e}")
        return None
    finally:
        try: restore_stderr(old_err)
        except: pass

def transcribe_audio_object(audio_data):
    """Turns a completed audio file object into text."""
    if not audio_data:
        return ""
    recognizer = sr.Recognizer()
    try:
        print("[Processing speech...]")
        text = recognizer.recognize_google(audio_data)
        print(f"You (Voice) >> {text}")
        return text
    except (sr.UnknownValueError, sr.RequestError):
        return ""

def wait_for_wake_word(trigger_phrase="hello"):
    """Blocks execution until the trigger phrase is heard without locking up."""
    old_err = suppress_alsa_errors()  
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  
    
    try:
        with sr.Microphone() as source:
            restore_stderr(old_err)  
            print(f"\n[Passive Listening... Say '{trigger_phrase}' to wake me up]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while True:
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio).lower()
                    
                    if trigger_phrase in text:
                        print(f"\nWake word '{trigger_phrase}' detected!")
                        return True
                except sr.WaitTimeoutError:
                    continue
                except (sr.UnknownValueError, sr.RequestError):
                    continue
    finally:
        try: restore_stderr(old_err)
        except: pass
