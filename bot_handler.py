from google import genai

class ChatBot:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        """Initializes the Gemini Client and starts a stateful chat session."""
        # This will automatically look for the GEMINI_API_KEY environment variable
        self.client = genai.Client()
        self.chat = self.client.chats.create(model=model_name)

    def send_message(self, message: str) -> str:
        """Sends a message to the bot and returns the text response."""
        response = self.chat.send_message(message)
        return response.text