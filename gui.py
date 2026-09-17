import tkinter as tk
from tkinter import scrolledtext
import threading
import math
import re
from bot_handler import ChatBot
from audio_handler import speak, stop_audio
from voice_handler import record_active_mic, transcribe_audio_object, wait_for_wake_word

from dotenv import load_dotenv
load_dotenv()

class OmniForgeAnimatedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OmniForge")
        self.root.geometry("480x630") 
        self.root.configure(bg="#0c0c0e")
        self.root.resizable(False, False)

        self.current_state = "idle"  
        self.anim_frame = 0          
        self.colors = {"idle": "#007acc", "listening": "#28a745", "thinking": "#ffc107", "speaking": "#dc3545"}
        self.wake_word_active = False

        try:
            self.bot = ChatBot()
            initial_status = "OmniForge Active"
        except Exception as e:
            initial_status = "Configuration Error"

        # 1. Main Status Text Label
        self.status_label = tk.Label(root, text=initial_status, fg="#ffffff", bg="#0c0c0e", font=("Arial", 16, "bold"), pady=10)
        self.status_label.pack(side=tk.TOP, fill=tk.X)

        # 2. Scrollable Display Window
        self.subtitle_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', bg="#141419", fg="#aaaaaa", font=("Arial", 11, "italic"), bd=0, highlightthickness=0, height=4)
        self.subtitle_display.pack(side=tk.TOP, padx=25, pady=5, fill=tk.X)
        self.update_subtitle_text("Tap the core to speak, or type your message below!")

        # 3. Canvas for Core Animations
        self.canvas_size = 180 
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="#0c0c0e", bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.TOP, pady=5)
        self.canvas.bind("<Button-1>", lambda event: self.trigger_voice_interaction())

        # 4. Keyboard Text Entry Section
        text_frame = tk.Frame(root, bg="#0c0c0e")
        text_frame.pack(fill=tk.X, side=tk.TOP, padx=25, pady=10)

        self.entry_field = tk.Entry(text_frame, bg="#1a1a24", fg="#ffffff", insertbackground="white", font=("Arial", 11), bd=0, highlightthickness=1, highlightbackground="#2d2d3d", highlightcolor="#007acc")
        self.entry_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 5))
        self.entry_field.bind("<Return>", lambda event: self.trigger_text_interaction())

        self.send_button = tk.Button(text_frame, text="Send", font=("Arial", 10, "bold"), bg="#007acc", fg="white", activebackground="#005999", activeforeground="white", bd=0, relief="flat", padx=15, command=self.trigger_text_interaction)
        self.send_button.pack(side=tk.RIGHT, ipady=4)

        # 5. Secondary Control Panel Panel
        control_frame = tk.Frame(root, bg="#0c0c0e")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20, padx=20)

        self.wake_button = tk.Button(control_frame, text="Turn On Wake Mode", font=("Arial", 10, "bold"), bg="#1a1a24", fg="#ffffff", activebackground="#2a2a35", activeforeground="white", bd=0, relief="flat", height=2, width=16, command=self.toggle_wake_word_mode)
        self.wake_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop Audio", font=("Arial", 10, "bold"), bg="#2d1414", fg="#ff6b6b", activebackground="#3d2424", activeforeground="#ff6b6b", bd=0, relief="flat", height=2, width=16, command=self.interrupt_speech)
        self.stop_button.pack(side=tk.RIGHT, expand=True, padx=5)

        self.render_animation_loop()

    def update_subtitle_text(self, text):
        self.subtitle_display.configure(state='normal')
        self.subtitle_display.delete("1.0", tk.END)
        self.subtitle_display.insert(tk.END, text)
        self.subtitle_display.tag_add("center", "1.0", "end")
        self.subtitle_display.tag_configure("center", justify='center')
        self.subtitle_display.configure(state='disabled')
        self.subtitle_display.see(tk.END)

    def render_animation_loop(self):
        self.canvas.delete("all")
        center = self.canvas_size / 2
        self.anim_frame += 1
        state = self.current_state
        color = self.colors.get(state, "#007acc")

        if state == "idle":
            pulse_modifier = math.sin(self.anim_frame * 0.05) * 10
            base_radius = 40 + pulse_modifier
            self.canvas.create_oval(center - base_radius - 8, center - base_radius - 8, center + base_radius + 8, center + base_radius + 8, outline=color, width=2)
            self.canvas.create_oval(center - 35, center - 35, center + 35, center + 35, fill=color, outline="")
        elif state == "listening":
            ripple_radius = 35 + (self.anim_frame % 20) * 2.5
            self.canvas.create_oval(center - ripple_radius, center - ripple_radius, center + ripple_radius, center + ripple_radius, outline=color, width=3)
            self.canvas.create_oval(center - 35, center - 35, center + 35, center + 35, fill=color, outline="")
        elif state == "thinking":
            self.canvas.create_oval(center - 40, center - 40, center + 40, center + 40, outline="#222222", width=4)
            angle = (self.anim_frame * 0.15) % (2 * math.pi)
            dot_x = center + math.cos(angle) * 40
            dot_y = center + math.sin(angle) * 40
            self.canvas.create_oval(center - 30, center - 30, center + 30, center + 30, fill="#1a1a24", outline="")
            self.canvas.create_oval(dot_x - 7, dot_y - 7, dot_x + 7, dot_y + 7, fill=color, outline="")
        elif state == "speaking":
            self.canvas.create_oval(center - 35, center - 35, center + 35, center + 35, fill=color, outline="")
            for i in range(-3, 4):
                offset_x = center + (i * 16)
                wave_height = abs(math.sin(self.anim_frame * 0.2 + i)) * 30 + 10
                self.canvas.create_line(offset_x, center - wave_height/2, offset_x, center + wave_height/2, fill=color, width=4)

        self.root.after(33, self.render_animation_loop)

    def trigger_voice_interaction(self):
        if self.current_state in ["listening", "thinking", "speaking"]:
            stop_audio()
        
        self.current_state = "listening"
        self.status_label.config(text="Listening...")
        self.update_subtitle_text("I'm listening. Speak your query...")
        
        threading.Thread(target=self.run_voice_pipeline, daemon=True).start()

    def trigger_text_interaction(self):
        user_text = self.entry_field.get().strip()
        if not user_text or self.current_state in ["listening", "thinking", "speaking"]:
            return
            
        self.entry_field.delete(0, tk.END)
        if self.current_state == "speaking":
            stop_audio()

        self.current_state = "thinking"
        self.status_label.config(text="Thinking...")
        self.update_subtitle_text(f'"{user_text}"')

        threading.Thread(target=self.run_processing_pipeline, args=(user_text,), daemon=True).start()

    def run_voice_pipeline(self):
        audio_captured = record_active_mic()
        if not audio_captured:
            self.reset_to_idle("No audio data received.")
            return

        self.current_state = "thinking"
        self.root.after(0, lambda: self.status_label.config(text="Thinking..."))
        self.root.after(0, lambda: self.update_subtitle_text("Processing speech files..."))

        user_voice_text = transcribe_audio_object(audio_captured)
        if not user_voice_text.strip():
            self.reset_to_idle("Could not interpret speech pattern.")
            return

        self.root.after(0, lambda: self.update_subtitle_text(f'"{user_voice_text}"'))
        self.run_processing_pipeline(user_voice_text)

    def run_processing_pipeline(self, prompt_text):
        try:
            bot_response = self.bot.send_message(prompt_text)
            self.current_state = "speaking"
            self.root.after(0, lambda: self.status_label.config(text="Speaking..."))
            self.root.after(0, lambda: self.update_subtitle_text(bot_response))
            speak(bot_response)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                match = re.search(r"retry in (\d+)", error_msg)
                wait_time = match.group(1) if match else "a few"
                clean_message = f"System: Daily Free Tier Limit Reached.\nPlease retry in {wait_time} seconds."
                self.reset_to_idle(clean_message)
            else:
                self.reset_to_idle("System: Connection error. Try again.")
            return

        self.reset_to_idle("Core ready. Tap to talk or type above!")

    def reset_to_idle(self, subtitle_msg):
        self.current_state = "idle"
        self.root.after(0, lambda: self.status_label.config(text="OmniForge Active"))
        self.root.after(0, lambda: self.update_subtitle_text(subtitle_msg))

    def toggle_wake_word_mode(self):
        if not self.wake_word_active:
            self.wake_word_active = True
            self.wake_button.config(text="Wake Mode: ON", bg="#0f3d1b", fg="#7fff7f")
            self.update_subtitle_text("Hands-free listening on. Say 'hello' to wake me up!")
            threading.Thread(target=self.background_wake_listener, daemon=True).start()
        else:
            self.wake_word_active = False
            self.wake_button.config(text="Turn On Wake Mode", bg="#1a1a24", fg="#ffffff")
            self.update_subtitle_text("Wake Mode turned off.")

    def background_wake_listener(self):
        while self.wake_word_active:
            detected = wait_for_wake_word("hello")
            if detected and self.wake_word_active:
                self.root.after(0, self.trigger_voice_interaction)
                break

    def interrupt_speech(self):
        stop_audio()
        self.reset_to_idle("Playback cancelled.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OmniForgeAnimatedGUI(root)
    root.mainloop()