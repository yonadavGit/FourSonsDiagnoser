import pyttsx3
import threading

class VoiceOverSpeaker:
    def __init__(self):
        # Initialize the TTS engine
        self.engine = pyttsx3.init()
        # Set properties for voice
        self._set_british_voice()
        # Set speech rate (optional)
        self.engine.setProperty('rate', 200)  # Speed of speech
        # Set volume (optional)
        self.engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

    def _set_british_voice(self):
        # Retrieve available voices
        voices = self.engine.getProperty('voices')
        # Iterate through voices to find a British English voice
        for voice in voices:
            if 'english' in voice.name.lower() and 'gb' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        else:
            raise ValueError("No British English voice found.")

    def speak(self, text):
        if self.engine._inLoop:
            self.engine.endLoop()
        self.engine.say(text)
        def speak_thread(text):
            self.engine.runAndWait()
        threading.Thread(target=speak_thread, args=(text,)).start()