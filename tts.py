import pyttsx3

class TextToSpeech:
    def __init__(self, rate=175, volume=0.9):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        voices = self.engine.getProperty("voices")
        if len(voices) > 1:
            self.engine.setProperty("voice", voices[0].id)

    def speak(self, text):
        print(f"TTS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
