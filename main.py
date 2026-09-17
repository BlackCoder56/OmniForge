import threading
from bot_handler import ChatBot
from audio_handler import speak
from voice_handler import listen_to_mic, wait_for_wake_word
from dotenv import load_dotenv

import time
import re


load_dotenv()


def process_interaction(bot, user_input):
    """Core logic wrapper to send prompt to Gemini and speak response."""
    if not user_input.strip():
        return
    try:
        bot_text = bot.send_message(user_input)
        print(f"Bot >> {bot_text}")
        speak(bot_text)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print("\n[System: Daily Free Tier Limit Reached]")
            
            # Try to extract the retry seconds from the error string dynamically
            match = re.search(r"retry in (\d+\.\d+)s", error_msg)
            wait_time = float(match.group(1)) if match else 30.0
            
            print(f"[System: Pausing voice requests. Retrying automatically in {int(wait_time)} seconds...]")
            time.sleep(wait_time)
        else:
            print(f"An error occurred: {e}")


def hands_free_loop(bot):
    """Background engine that continuously waits for the wake word."""
    print("\n--- Hands-Free Wake Word Mode Activated ---")
    while True:
        # 1. Block until "Hey OmniForge" is spoken
        wait_for_wake_word("hello")
        
        # 2. Trigger the active voice recorder for your command
        user_voice_input = listen_to_mic()
        
        # 3. Process it
        if user_voice_input.strip():
            process_interaction(bot, user_voice_input)

def main():
    print("Initializing OmniForge...")
    try:
        bot = ChatBot()
        print("OmniForge ready!")
        print("\nOptions:")
        print("1. Just type normally below.")
        print("2. Enter 'v' to manually record a voice prompt.")
        print("3. Enter 'wake' to turn on hands-free background listening.")
        print("Type 'quit' or 'exit' to stop.")
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        return

    while True:
        user_input = input("\nYou >> ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        if user_input.lower() == 'v':
            user_input = listen_to_mic()
            process_interaction(bot, user_input)
            continue
            
        if user_input.lower() == 'wake':
            # Run the wake word loop on a daemon thread so it doesn't lock up the terminal
            wake_thread = threading.Thread(target=hands_free_loop, args=(bot,), daemon=True)
            wake_thread.start()
            print("[System: Wake word engine running in background. You can still type queries here!]")
            continue

        # Standard manual text typing path
        process_interaction(bot, user_input)

if __name__ == "__main__":
    main()