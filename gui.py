import tkinter as tk
import threading
from bot_handler import ChatBot
from audio_handler import speak, stop_audio  # Added stop_audio import
from voice_handler import listen_to_mic, wait_for_wake_word

from dotenv import load_dotenv
load_dotenv()

class OmniForgeVoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OmniForge Voice")
        self.root.geometry("400x480")
        self.root.configure(bg="#121212")

        # Configuration States
        self.color_idle = "#007acc"      
        self.color_listening = "#28a745" 
        self.color_thinking = "#ffc107"  
        self.color_speaking = "#dc3545"  
        
        self.wake_word_active = False    # Tracks if passive listening is running

        try:
            self.bot = ChatBot()
            initial_status = "Ready"
        except Exception as e:
            initial_status = "Initialization Error"

        # 1. Main Status Indicator
        self.status_label = tk.Label(
            root, text=initial_status, fg="#ffffff", bg="#121212", 
            font=("Arial", 16, "bold"), pady=20
        )
        self.status_label.pack()

        # 2. Dynamic Central Subtitle
        self.subtitle_label = tk.Label(
            root, text="Tap the button below or turn on Wake Mode to start.", 
            fg="#aaaaaa", bg="#121212", font=("Arial", 11), 
            wraplength=340, justify="center", pady=10
        )
        self.subtitle_label.pack(fill=tk.BOTH, expand=True)

        # 3. Big Central Voice Button
        self.action_button = tk.Button(
            root, text="Tap to Speak", font=("Arial", 14, "bold"),
            bg=self.color_idle, fg="white", activebackground="#005999", activeforeground="white",
            bd=0, relief="flat", height=3, width=18,
            command=self.trigger_interaction
        )
        self.action_button.pack(pady=20)

        # 4. Secondary Control Panel Frame (Bottom Buttons)
        control_frame = tk.Frame(root, bg="#121212")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=30, padx=20)

        # Wake Word Toggle Button
        self.wake_button = tk.Button(
            control_frame, text="Turn On Wake Mode", font=("Arial", 10, "bold"),
            bg="#333333", fg="#ffffff", bd=0, relief="flat", height=2, width=16,
            command=self.toggle_wake_word_mode
        )
        self.wake_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Stop Playback Button
        self.stop_button = tk.Button(
            control_frame, text="Stop Audio", font=("Arial", 10, "bold"),
            bg="#441111", fg="#ff9999", bd=0, relief="flat", height=2, width=16,
            command=self.interrupt_speech
        )
        self.stop_button.pack(side=tk.RIGHT, expand=True, padx=5)

    def update_ui_state(self, status_text, subtitle_text, button_text, button_color, button_enabled=True):
        """Safely updates UI elements across threads."""
        self.status_label.config(text=status_text)
        self.subtitle_label.config(text=subtitle_text)
        self.action_button.config(
            text=button_text, 
            bg=button_color, 
            state='normal' if button_enabled else 'disabled'
        )

    def trigger_interaction(self):
        """Manual interaction pipeline when button is clicked."""
        stop_audio()  # Stop talking if user interrupts by clicking
        self.update_ui_state("Listening...", "Say something to OmniForge...", "Listening...", self.color_listening, button_enabled=False)
        threading.Thread(target=self.run_voice_pipeline, daemon=True).start()

    def run_voice_pipeline(self):
        """Background loop handling speech capture, AI processing, and audio output."""
        user_voice_text = listen_to_mic()
        
        if not user_voice_text.strip():
            self.root.after(0, lambda: self.update_ui_state("Ready", "I didn't hear anything. Try again!", "Tap to Speak", self.color_idle))
            return

        self.root.after(0, lambda: self.update_ui_state("Thinking...", f'"{user_voice_text}"', "Thinking...", self.color_thinking, button_enabled=False))

        try:
            bot_response = self.bot.send_message(user_voice_text)
            self.root.after(0, lambda: self.update_ui_state("Speaking...", bot_response, "Speaking...", self.color_speaking, button_enabled=False))
            speak(bot_response)
        except Exception as e:
            self.root.after(0, lambda: self.update_ui_state("Error", f"Issue: {e}", "Tap to Speak", self.color_idle))
            return

        self.root.after(0, lambda: self.update_ui_state("Ready", "Tap or speak the wake word to chat again.", "Tap to Speak", self.color_idle))

    def toggle_wake_word_mode(self):
        """Turns the background passive listening engine on or off."""
        if not self.wake_word_active:
            self.wake_word_active = True
            self.wake_button.config(text="Wake Mode: ON", bg="#155724", fg="#d4edda")
            self.subtitle_label.config(text="Wake Mode activated. Say 'hello' out loud to speak!")
            threading.Thread(target=self.background_wake_listener, daemon=True).start()
        else:
            self.wake_word_active = False
            self.wake_button.config(text="Turn On Wake Mode", bg="#333333", fg="#ffffff")
            self.subtitle_label.config(text="Wake Mode deactivated.")

    def background_wake_listener(self):
        """Passive daemon engine running loop for wake word."""
        while self.wake_word_active:
            # Block until "hello" is parsed or loop is toggled off
            detected = wait_for_wake_word("hello")
            
            # Double check that user hasn't turned off mode mid-listening phase
            if detected and self.wake_word_active:
                # Trigger the exact same communication pipeline hands-free!
                self.root.after(0, self.trigger_interaction)
                break  # Exit this loop instance; pipeline completion resets standard state

    def interrupt_speech(self):
        """Triggers direct audio cancellation."""
        stop_audio()
        self.update_ui_state("Ready", "Audio playback cancelled.", "Tap to Speak", self.color_idle)

if __name__ == "__main__":
    root = tk.Tk()
    app = OmniForgeVoiceGUI(root)
    root.mainloop()