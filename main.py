from bot_handler import ChatBot
from audio_handler import speak
from voice_handler import listen_to_mic  # Import the new voice module
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Initializing chatbot... (Make sure GEMINI_API_KEY is set)")
    
    try:
        bot = ChatBot()
        print("Chatbot ready!")
        print("Options: Type your message, or press 'v' then Enter to use Voice.")
        print("Type 'quit' or 'exit' to stop.")
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        return

    while True:
        # Prompting for user method selection or immediate typing
        user_input = input("\nYou (Type, or enter 'v' for Voice) >> ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        # If user opts for voice mode
        if user_input.lower() == 'v':
            user_input = listen_to_mic()
            
        # Skip loop iteration if both typing or voice returned empty inputs
        if not user_input.strip():
            continue

        try:
            # 1. Get response from Gemini
            bot_text = bot.send_message(user_input)
            print(f"Bot >> {bot_text}")
            
            # 2. Speak the response out loud (now 25% faster!)
            speak(bot_text)
            
        except Exception as e:
            print(f"An error occurred during the chat: {e}")

if __name__ == "__main__":
    main()