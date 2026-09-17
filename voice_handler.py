import os
import sys
import speech_recognition as sr

def suppress_alsa_errors():
    """Redirects standard error to hide annoying ALSA/JACK logs."""
    # This works on Linux/macOS to silence C-level warnings
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

def listen_to_mic():
    """Listens to the microphone and returns transcribed text for a prompt."""
    old_err = suppress_alsa_errors()  # HIDE LOGS
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            restore_stderr(old_err)  # RESTORE LOGS FOR APPLICATION DEBUGS
            print("\n[Listening... Speak now]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("[Processing speech...]")
            text = recognizer.recognize_google(audio)
            print(f"You (Voice) >> {text}")
            return text
    except sr.WaitTimeoutError:
        print("[System: No speech detected.]")
        return ""
    except sr.UnknownValueError:
        print("[System: Could not understand audio.]")
        return ""
    except sr.RequestError as e:
        print(f"[System: Service error: {e}]")
        return ""
    finally:
        try: restore_stderr(old_err)
        except: pass

def wait_for_wake_word(trigger_phrase="hello"):
    """Blocks execution until the trigger phrase is heard without locking up."""
    old_err = suppress_alsa_errors()  # HIDE LOGS
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  # Let it adapt to your room noise dynamically
    
    try:
        with sr.Microphone() as source:
            restore_stderr(old_err)  # RESTORE LOGS
            print(f"\n[Passive Listening... Say '{trigger_phrase}' to wake me up]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while True:
                try:
                    # ADDED TIMEOUT HERE (2 seconds) so it never gets stuck in a loop forever
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio).lower()
                    
                    if trigger_phrase in text:
                        print(f"\n✨ Wake word '{trigger_phrase}' detected! ✨")
                        return True
                except sr.WaitTimeoutError:
                    # This lets the loop loop seamlessly instead of blocking infinitely
                    continue
                except (sr.UnknownValueError, sr.RequestError):
                    continue
    finally:
        try: restore_stderr(old_err)
        except: pass