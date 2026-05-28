import ollama
import json

SYSTEM_PROMPT = """You are J.A.R.V.I.S., a sophisticated, authoritative, and proactive AI assistant for Windows. 
You prioritize technical precision, architectural insight, and efficiency. 
Address the user as 'Sir' occasionally but maintain a professional administrative demeanor.

RESPOND WITH JSON ONLY.

ACTIONS:
- "open_app": app values: notepad, calculator, browser, vscode, whatsapp, explorer, settings, terminal, powershell
- "search_web": params: {"query": "search terms", "engine": "google" or "youtube"}
- "open_url": params: {"url": "https://..."}
- "read_clipboard": no params. Reads text from clipboard.
- "write_clipboard": params: {"text": "text to copy"}
- "create_folder": params: {"path": "full folder path"}
- "create_file": params: {"path": "full file path", "content": "text"}
- "list_dir": params: {"path": "directory path"}
- "delete_file": params: {"path": "file path"}
- "run_command": params: {"command": "cmd"}
- "speak": just chat/answer. params: {"text": "your answer"}

ALWAYS include: "action", "params", "response" (where "response" is what you will say to the user while performing the action).

EXAMPLES:
"Open calculator" -> {"action":"open_app","params":{"app":"calculator"},"response":"Opening the calculator for you, Sir."}
"Search for U2 band" -> {"action":"search_web","params":{"query":"U2 band"},"response":"Searching for the U2 band now, Sir."}
"What is in my clipboard?" -> {"action":"read_clipboard","params":{},"response":"Retrieving clipboard data, Sir."}
"Copy 'Hello World'" -> {"action":"write_clipboard","params":{"text":"Hello World"},"response":"Writing to your clipboard, Sir."}

Keep responses elite, professional, and slightly formal.
"""

class LLMBain:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def process(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = ollama.chat(
            model=self.model,
            messages=self.conversation_history,
            format="json",
            options={"temperature": 0.3}
        )
        
        result_text = response["message"]["content"]
        self.conversation_history.append({"role": "assistant", "content": result_text})
        
        try:
            clean = result_text.strip()
            clean = clean.replace("```json", "").replace("```", "").strip()
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            result = json.loads(clean)
            if "action" not in result:
                result = {"action": "speak", "params": {"text": result_text}, "response": result_text}
        except (json.JSONDecodeError, Exception):
            result = {"action": "speak", "params": {"text": result_text}, "response": result_text}
        
        return result

    def reset(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
