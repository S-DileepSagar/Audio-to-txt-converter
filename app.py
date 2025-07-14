import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from google import genai
import sounddevice as sd
import scipy.io.wavfile as wav

API_KEY = "AIzaSyDurxLEf4EVkmlHbWrcFOFzkmpKij5RtwM"  # <-- Replace with your actual Gemini API key
client = genai.Client(api_key=API_KEY)

def transcribe_audio(file_path):
    """Upload an audio file to Gemini and return its transcription."""
    audio_file = client.files.upload(file=file_path)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["Transcribe the audio.", audio_file]
    )
    return response.text

def translate_text(text, source_lang, target_lang):
    """Translate text between English and Telugu using Gemini."""
    if source_lang == target_lang:
        return text  # No translation needed
    # Construct a translation prompt based on source/target
    if source_lang == "English" and target_lang == "Telugu":
        prompt = f"Translate this English text to Telugu: {text}"
    elif source_lang == "Telugu" and target_lang == "English":
        prompt = f"Translate this Telugu text to English: {text}"
    else:
        return "Unsupported language selection."
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def record_audio(duration=15, fs=16000):
    """Record audio from the microphone for 'duration' seconds and save as 'temp.wav'."""
    try:
        sd.check_input_settings()
         # Check if microphone is available
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16',
                           )

        sd.wait()  # Wait until recording is finished
        wav.write("temp.wav", fs, recording)
        return "temp.wav"
    except Exception as e:
        messagebox.showerror("Recording Error", str(e))
        return None

def process_microphone():
    """Handle microphone input: record, transcribe, translate, and update UI."""
    file_path = record_audio()
    if not file_path:
        return
    transcript = transcribe_audio(file_path)
    app.source_text.delete(1.0, tk.END)
    app.source_text.insert(tk.END, transcript)
    translation = translate_text(transcript, app.source_lang.get(), app.target_lang.get())
    app.target_text.delete(1.0, tk.END)
    app.target_text.insert(tk.END, translation)

def process_file():
    """Handle file input: load/convert file, transcribe, translate, and update UI."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Media files", "*.wav *.mp3 *.mp4 *.mkv *.avi"), ("All files","*.*")]
    )
    if not file_path:
        return

    audio_path = file_path
    transcript = transcribe_audio(audio_path)
    app.source_text.delete(1.0, tk.END)
    app.source_text.insert(tk.END, transcript)
    translation = translate_text(transcript, app.source_lang.get(), app.target_lang.get())
    app.target_text.delete(1.0, tk.END)
    app.target_text.insert(tk.END, translation)

def start_translation():
    """Start the transcription/translation process on a new thread (to keep UI responsive)."""
    if app.input_type.get() == "Microphone":
        threading.Thread(target=process_microphone, daemon=True).start()
    else:
        threading.Thread(target=process_file, daemon=True).start()

class TranslatorApp(tk.Tk):
    """Tkinter GUI application."""
    def __init__(self):
        super().__init__()
        self.title("English–Telugu Real-Time Translator")
        # Input type: Microphone or File
        self.input_type = tk.StringVar(value="Microphone")
        tk.Radiobutton(self, text="Microphone", variable=self.input_type, value="Microphone").grid(row=0, column=0)
        tk.Radiobutton(self, text="File", variable=self.input_type, value="File").grid(row=0, column=1)
        # Language selection: source and target
        self.source_lang = tk.StringVar(value="English")
        self.target_lang = tk.StringVar(value="Telugu")
        tk.Label(self, text="Source:").grid(row=1, column=0)
        tk.OptionMenu(self, self.source_lang, "English", "Telugu").grid(row=1, column=1)
        tk.Label(self, text="Target:").grid(row=1, column=2)
        tk.OptionMenu(self, self.target_lang, "English", "Telugu").grid(row=1, column=3)
        # Translate button
        tk.Button(self, text="Translate", command=start_translation).grid(row=2, column=0, columnspan=4, pady=5)
        # Text areas for original and translated text
        tk.Label(self, text="Original Text").grid(row=3, column=0, columnspan=2)
        tk.Label(self, text="Translated Text").grid(row=3, column=2, columnspan=2)
        self.source_text = tk.Text(self, height=10, width=40)
        self.source_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.target_text = tk.Text(self, height=10, width=40)
        self.target_text.grid(row=4, column=2, columnspan=2, padx=5, pady=5)

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
