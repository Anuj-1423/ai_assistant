from ai_assistant.stt import SpeechToText
from ai_assistant.llm import LLMBain
from ai_assistant.actions import ActionEngine
from ai_assistant.tts import TextToSpeech

class VoiceAgent:
    def __init__(self, llm_model="llama3.2", whisper_model="base"):
        print("Initializing Voice Agent...")
        self.stt = SpeechToText(model_size=whisper_model)
        self.llm = LLMBain(model=llm_model)
        self.actions = ActionEngine()
        self.tts = TextToSpeech()
        self.running = False

    def run_voice_mode(self):
        self.running = True
        self.tts.speak("Systems online. J.A.R.V.I.S. is at your service, Sir.")

        while self.running:
            try:
                text = self.stt.listen()
                if not text or text.strip() == "":
                    continue

                print(f"You said: {text}")

                if text.lower() in ("stop", "exit", "quit", "shut down", "goodbye"):
                    self.tts.speak("Shutting down. Goodbye!")
                    break

                self._process_command(text, voice_mode=True)
            except KeyboardInterrupt:
                self.tts.speak("Shutting down.")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.tts.speak("Something went wrong. Please try again.")

    def run_text_mode(self):
        self.running = True
        print("Text mode. Type commands (or 'quit' to exit):")

        while self.running:
            try:
                text = input("You: ").strip()
                if not text:
                    continue
                if text.lower() in ("quit", "exit", "stop"):
                    print("Shutting down.")
                    break

                self._process_command(text, voice_mode=False)
            except KeyboardInterrupt:
                print("\nShutting down.")
                break

    def _process_command(self, text, voice_mode=False):
        try:
            decision = self.llm.process(text)
        except Exception:
            msg = "I've encountered a logic error, Sir. Please try again."
            self.tts.speak(msg) if voice_mode else print(f"Agent: {msg}")
            return

        action = decision.get("action", "speak")
        params = decision.get("params", {})
        response = decision.get("response", "Acknowledged, Sir.")

        # Narrate what he's about to do
        self.tts.speak(response) if voice_mode else print(f"Agent: {response}")

        if action == "speak":
            return

        # Handle Confirmations
        if action in ("delete_file", "run_command"):
            confirm_msg = "Awaiting confirmation for system execution, Sir."
            if voice_mode:
                self.tts.speak(confirm_msg)
                confirm = self.stt.listen()
                if not confirm or confirm.lower() not in ("yes", "yeah", "sure", "go ahead", "confirm", "do it", "ok", "okay"):
                    self.tts.speak("Operation cancelled.")
                    return
            else:
                print(f"Agent: {confirm_msg}")
                choice = input("[CONFIRM] Proceed, Sir? (yes/no): ").strip().lower()
                if choice not in ("yes", "y"):
                    print("Agent: Operation cancelled.")
                    return

        # Execute
        try:
            result = self.actions.execute(action, params if params else {})
        except Exception as e:
            result = f"Task failed, Sir: {str(e)}"

        # Report result
        if result:
            self.tts.speak(result) if voice_mode else print(f"Agent: {result}")

if __name__ == "__main__":
    agent = VoiceAgent()

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--text":
        agent.run_text_mode()
    else:
        agent.run_voice_mode()
