from google import genai
from google.genai import types

class ChatBot:
    def __init__(self):
        # Initializes the client using the GEMINI_API_KEY environment variable automatically
        self.client = genai.Client()
        self.model_name = 'gemini-3.6-flash'
        
        # Define a strict, human-like voice assistant personality
        self.config = types.GenerateContentConfig(
            system_instruction=(
                "You are OmniForge, a friendly, human-like voice assistant. "
                "CRITICAL: Keep your responses highly conversational, natural, and extremely concise. "
                "Never write long paragraphs or essays. Limit your responses to a maximum of 1 to 2 sentences. "
                "If the user asks for a complex breakdown, summarize it instantly into a punchy overview. "
                "Do not use markdown formatting like asterisks or bullet points, as your response will be read out loud."
            ),
            temperature=0.7 # Slight randomness makes it feel less robotic
        )
        
        # Start a chat session so it remembers conversation history
        self.chat = self.client.chats.create(model=self.model_name, config=self.config)

    def send_message(self, prompt):
        """Sends the user message to the active chat session."""
        response = self.chat.send_message(prompt)
        return response.text