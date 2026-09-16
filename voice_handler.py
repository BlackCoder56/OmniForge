import speech_recognition as sr

def listen_to_mic():
    """Listens to the microphone and returns the transcribed text."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n[Listening... Speak now]")
        # Adjust for ambient background noise automatically
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("[Processing speech...]")
            text = recognizer.recognize_google(audio)
            print(f"You (Voice) >> {text}")
            return text
        except sr.WaitTimeoutError:
            print("[System: Listening timed out. No speech detected.]")
            return ""
        except sr.UnknownValueError:
            print("[System: Could not understand the audio. Please try again.]")
            return ""
        except sr.RequestError as e:
            print(f"[System: Speech recognition service error: {e}]")
            return ""
