from bot_handler import ChatBot
from audio_handler import speak

from dotenv import load_dotenv
# Automatically load environment variables from the .env file
load_dotenv()


def main():
    print("Initializing chatbot... (Make sure GEMINI_API_KEY is set)")
    
    try:
        bot = ChatBot()
        print("Chatbot ready! Type 'quit' or 'exit' to stop.")
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        return

    while True:
        user_input = input("\nYou >> ")
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            continue

        try:
            # 1. Get response from Gemini
            bot_text = bot.send_message(user_input)
            print(f"Bot >> {bot_text}")
            
            # 2. Speak the response out loud
            speak(bot_text)
            
        except Exception as e:
            print(f"An error occurred during the chat: {e}")

if __name__ == "__main__":
    main()