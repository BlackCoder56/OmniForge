import customtkinter as ctk
import tkinter as tk
import threading
import math
import re
from bot_handler import ChatBot
from audio_handler import speak, stop_audio
from voice_handler import record_active_mic, transcribe_audio_object, wait_for_wake_word

from dotenv import load_dotenv
load_dotenv()

# Set modern global themes
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OmniForgeModernGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OmniForge Companion")
        self.geometry("420x660")
        self.configure(fg_color="#08080a") # Deep premium OLED background
        self.resizable(False, False)

        # Animation states
        self.current_state = "idle"  
        self.anim_frame = 0          
        self.colors = {
            "idle": "#007acc",
            "listening": "#28a745",
            "thinking": "#ffc107",
            "speaking": "#dc3545"
        }
        self.wake_word_active = False

        try:
            self.bot = ChatBot()
            initial_status = "OmniForge Active"
        except Exception as e:
            initial_status = "Configuration Error"

        # 1. Premium Status Label
        self.status_label = ctk.CTkLabel(
            self, text=initial_status, font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#ffffff"
        )
        self.status_label.pack(side=tk.TOP, pady=(20, 5))

        # 2. Sleek Borderless Text Box
        self.subtitle_display = ctk.CTkTextbox(
            self, width=370, height=80, font=ctk.CTkFont(family="Arial", size=13, style="italic"),
            fg_color="#111115", text_color="#aaaaaa", border_width=0, corner_radius=12
        )
        self.subtitle_display.pack(side=tk.TOP, padx=25, pady=10)
        self.update_subtitle_text("Tap the core to speak, or type your message below.")

        # 3. Canvas for Advanced Layered Core Animations
        self.canvas_size = 200
        self.canvas = tk.Canvas(
            self, width=self.canvas_size, height=self.canvas_size, 
            bg="#08080a", bd=0, highlightthickness=0
        )
        self.canvas.pack(side=tk.TOP, pady=10)
        self.canvas.bind("<Button-1>", lambda event: self.trigger_voice_interaction())

        # 4. Modern Input Field with Rounded Corners
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(fill=tk.X, side=tk.TOP, padx=25, pady=15)

        self.entry_field = ctk.CTkEntry(
            text_frame, placeholder_text="Ask OmniForge anything...",
            fg_color="#16161f", text_color="#ffffff", border_color="#2d2d3d",
            corner_radius=20, height=40, font=ctk.CTkFont(family="Arial", size=13)
        )
        self.entry_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_field.bind("<Return>", lambda event: self.trigger_text_interaction())

        self.send_button = ctk.CTkButton(
            text_frame, text="Send", width=80, height=40, corner_radius=20,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            fg_color="#007acc", hover_color="#005999", command=self.trigger_text_interaction
        )
        self.send_button.pack(side=tk.RIGHT)

        # 5. Bottom Control Deck Panel
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=25, padx=25)

        self.wake_button = ctk.CTkButton(
            control_frame, text="Turn On Wake Mode", height=45, corner_radius=12,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            fg_color="#16161f", hover_color="#22222f", text_color="#ffffff",
            border_width=1, border_color="#2d2d3d", command=self.toggle_wake_word_mode
        )
        self.wake_button.pack(side=tk.LEFT, expand=True, padx=(0, 5), fill=tk.X)

        self.stop_button = ctk.CTkButton(
            control_frame, text="Stop Audio", height=45, corner_radius=12,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            fg_color="#210f0f", hover_color="#361717", text_color="#ff6b6b",
            command=self.interrupt_speech
        )
        self.stop_button.pack(side=tk.RIGHT, expand=True, padx=(5, 0), fill=tk.X)

        self.render_animation_loop()

    def update_subtitle_text(self, text):
        self.subtitle_display.configure(state='normal')
        self.subtitle_display.delete("1.0", tk.END)
        self.subtitle_display.insert(tk.END, text)
        self.subtitle_display.configure(state='disabled')

    def render_animation_loop(self):
        """Renders an attractive, multi-layered fluid wave on a vector canvas."""
        self.canvas.delete("all")
        center = self.canvas_size / 2
        self.anim_frame += 1
        state = self.current_state
        color = self.colors.get(state, "#007acc")

        if state == "idle":
            # 💤 Dual breath overlay aura (creates depth)
            wave1 = math.sin(self.anim_frame * 0.04) * 10
            wave2 = math.cos(self.anim_frame * 0.06) * 6
            
            self.canvas.create_oval(center - (45 + wave1), center - (45 + wave1), center + (45 + wave1), center + (45 + wave1), outline=color, width=1)
            self.canvas.create_oval(center - (38 + wave2), center - (38 + wave2), center + (38 + wave2), center + (38 + wave2), outline=color, width=2)
            self.canvas.create_oval(center - 30, center - 30, center + 30, center + 30, fill=color, outline="")

        elif state == "listening":
            # 🎙️ Multi-ring expanding sound ripple
            for i in range(3):
                ripple_radius = 30 + ((self.anim_frame + (i * 8)) % 24) * 2.5
                alpha_width = max(1, 3 - i)
                self.canvas.create_oval(center - ripple_radius, center - ripple_radius, center + ripple_radius, center + ripple_radius, outline=color, width=alpha_width)
            self.canvas.create_oval(center - 30, center - 30, center + 30, center + 30, fill=color, outline="")

        elif state == "thinking":
            # 🧠 Glowing twin-dot orbital tracking rings
            self.canvas.create_oval(center - 40, center - 40, center + 40, center + 40, outline="#16161f", width=4)
            angle1 = (self.anim_frame * 0.12) % (2 * math.pi)
            angle2 = (self.anim_frame * -0.08) % (2 * math.pi)
            
            dx1, dy1 = center + math.cos(angle1) * 40, center + math.sin(angle1) * 40
            dx2, dy2 = center + math.cos(angle2) * 40, center + math.sin(angle2) * 40
            
            self.canvas.create_oval(center - 25, center - 25, center + 25, center + 25, fill="#111115", outline="")
            self.canvas.create_oval(dx1 - 6, dy1 - 6, dx1 + 6, dy1 + 6, fill=color, outline="")
            self.canvas.create_oval(dx2 - 4, dy2 - 4, dx2 + 4, dy2 + 4, fill="#ffffff", outline="")

        elif state == "speaking":
            # 🔊 Organic, fluidly undulating equalizer bands
            self.canvas.create_oval(center - 30, center - 30, center + 30, center + 30, fill=color, outline="")
            for i in range(-4, 5):
                offset_x = center + (i * 14)
                # Combines sine and cosine to create a beautiful fluid audio jump
                wave_height = abs(math.sin(self.anim_frame * 0.15 + i) * math.cos(self.anim_frame * 0.08)) * 45 + 8
                self.canvas.create_line(offset_x, center - wave_height/2, offset_x, center + wave_height/2, fill=color, width=4)

        self.after(33, self.render_animation_loop)

    def trigger_voice_interaction(self):
        if self.current_state in ["listening", "thinking", "speaking"]:
            stop_audio()
        self.current_state = "listening"
        self.status_label.configure(text="Listening...")
        self.update_subtitle_text("I'm listening. Speak your query...")
        threading.Thread(target=self.run_voice_pipeline, daemon=True).start()

    def trigger_text_interaction(self):
        user_text = self.entry_field.get().strip()
        if not user_text or self.current_state in ["listening", "thinking", "speaking"]:
            return
            
        self.entry_field.delete(0, tk.END)
        self.current_state = "thinking"
        self.status_label.configure(text="Thinking...")
        self.update_subtitle_text(f'"{user_text}"')
        threading.Thread(target=self.run_processing_pipeline, args=(user_text,), daemon=True).start()

    def run_voice_pipeline(self):
        audio_captured = record_active_mic()
        if not audio_captured:
            self.reset_to_idle("No audio data received.")
            return

        self.current_state = "thinking"
        self.after(0, lambda: self.status_label.configure(text="Thinking..."))
        self.after(0, lambda: self.update_subtitle_text("Processing speech files..."))

        user_voice_text = transcribe_audio_object(audio_captured)
        if not user_voice_text.strip():
            self.reset_to_idle("Could not interpret speech pattern.")
            return

        self.after(0, lambda: self.update_subtitle_text(f'"{user_voice_text}"'))
        self.run_processing_pipeline(user_voice_text)

    def run_processing_pipeline(self, prompt_text):
        try:
            bot_response = self.bot.send_message(prompt_text)
            self.current_state = "speaking"
            self.after(0, lambda: self.status_label.configure(text="Speaking..."))
            self.after(0, lambda: self.update_subtitle_text(bot_response))
            speak(bot_response)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                match = re.search(r"retry in (\d+)", error_msg)
                wait_time = match.group(1) if match else "a few"
                self.reset_to_idle(f"System: Daily Limit Reached. Retry in {wait_time}s.")
            else:
                self.reset_to_idle("System: Connection error. Try again.")
            return

        self.reset_to_idle("Ready. Tap to talk or type above!")

    def reset_to_idle(self, subtitle_msg):
        self.current_state = "idle"
        self.after(0, lambda: self.status_label.configure(text="OmniForge Active"))
        self.after(0, lambda: self.update_subtitle_text(subtitle_msg))

    def toggle_wake_word_mode(self):
        if not self.wake_word_active:
            self.wake_word_active = True
            self.wake_button.configure(text="Wake Mode: ON", fg_color="#0f3d1b", hover_color="#0a2912", text_color="#7fff7f")
            self.update_subtitle_text("Hands-free listening on. Say 'hello' to wake me up!")
            threading.Thread(target=self.background_wake_listener, daemon=True).start()
        else:
            self.wake_word_active = False
            self.wake_button.configure(text="Turn On Wake Mode", fg_color="#16161f", hover_color="#22222f", text_color="#ffffff")
            self.update_subtitle_text("Wake Mode turned off.")

    def background_wake_listener(self):
        while self.wake_word_active:
            detected = wait_for_wake_word("hello")
            if detected and self.wake_word_active:
                self.after(0, self.trigger_voice_interaction)
                break

    def interrupt_speech(self):
        stop_audio()
        self.reset_to_idle("Playback cancelled.")

if __name__ == "__main__":
    app = OmniForgeModernGUI()
    app.mainloop()
