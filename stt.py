import sounddevice as sd
import numpy as np
import time
from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="medium"):
        print(f"Loading Whisper model ({model_size})...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.sample_rate = 16000
        self.channels = 1
        self.energy_threshold = 0.015
        self.silence_timeout = 5.0
        self.max_duration = 60

    def record_with_vad(self):
        print("Listening... (speak now)")
        
        all_audio = []
        chunk_duration = 0.2
        chunk_size = int(self.sample_rate * chunk_duration)
        
        speaking = False
        silence_start_time = None
        start_time = None
        
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=chunk_size
        )
        stream.start()
        
        try:
            while True:
                chunk, overflowed = stream.read(chunk_size)
                chunk = chunk[:, 0]
                
                energy = np.mean(np.abs(chunk))
                is_speech = energy > self.energy_threshold
                
                if is_speech and not speaking:
                    speaking = True
                    silence_start_time = None
                    start_time = time.time()
                    print("Voice detected...")
                
                if speaking:
                    all_audio.append(chunk)
                    
                    if is_speech:
                        silence_start_time = None
                    else:
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time > self.silence_timeout:
                            print("Silence detected. Processing...")
                            break
                    
                    total_time = len(all_audio) * chunk_duration
                    if total_time > self.max_duration:
                        print("Max duration reached.")
                        break
                else:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time > 30:
                        print("Timeout. No speech detected.")
                        return None
                        
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            stream.stop()
            stream.close()
        
        if not all_audio:
            return None
            
        audio = np.concatenate(all_audio)
        print(f"Recorded {len(audio)/self.sample_rate:.1f}s of audio.")
        return audio

    def transcribe(self, audio):
        segments, info = self.model.transcribe(audio, beam_size=5, language="en")
        text = " ".join([seg.text for seg in segments]).strip()
        return text

    def listen(self):
        try:
            audio = self.record_with_vad()
            if audio is None:
                return None
            
            energy = np.mean(np.abs(audio))
            if energy < self.energy_threshold * 0.5:
                print("No speech detected.")
                return None
                
            return self.transcribe(audio)
        except Exception as e:
            print(f"Recording error: {e}")
            return None
