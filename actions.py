import os
import subprocess
import urllib.parse
import psutil
import pyperclip

APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "browser": "start microsoft-edge:",
    "vscode": "code .",
    "whatsapp": "start microsoft-edge:https://web.whatsapp.com",
    "explorer": "explorer.exe",
    "settings": "start ms-settings:",
    "terminal": "start cmd",
    "powershell": "start powershell",
}

class ActionEngine:
    def __init__(self):
        self.confirmation_required = ["delete_file", "run_command"]

    def execute(self, action, params, confirm_callback=None):
        action = action.lower()
        
        if action in self.confirmation_required:
            if confirm_callback:
                msg = "Confirm deletion" if action == "delete_file" else "Confirm command execution"
                if not confirm_callback(msg):
                    return "Action cancelled by user."
        
        actions_map = {
            "open_app": self.open_app,
            "open_file": self.open_file,
            "create_folder": self.create_folder,
            "create_file": self.create_file,
            "read_file": self.read_file,
            "list_dir": self.list_dir,
            "delete_file": self.delete_file,
            "run_command": self.run_command,
            "speak": lambda p: p.get("text", "Done."),
            "code_task": self.code_task,
            "search_web": self.search_web,
            "open_url": self.open_url,
            "read_clipboard": self.read_clipboard,
            "write_clipboard": self.write_clipboard,
        }
        
        handler = actions_map.get(action)
        if not handler:
            return f"I do not know how to do that yet."
        
        try:
            result = handler(params if params else {})
            return result
        except Exception as e:
            return f"Could not complete that action: {str(e)}"

    def open_app(self, params):
        app = params.get("app", "").lower()
        cmd = APP_PATHS.get(app)
        if not cmd:
            return f"I can open these apps: {', '.join(APP_PATHS.keys())}"
        subprocess.Popen(cmd, shell=True)
        return f"Opened {app}."

    def search_web(self, params):
        query = params.get("query", "")
        engine = params.get("engine", "google")
        if engine == "youtube":
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        subprocess.Popen(f"start microsoft-edge:{url}", shell=True)
        return f"Searched '{query}' on {engine}."

    def open_url(self, params):
        url = params.get("url", "")
        subprocess.Popen(f"start microsoft-edge:{url}", shell=True)
        return f"Opened {url}."

    def open_file(self, params):
        path = params["path"]
        if os.path.exists(path):
            os.startfile(path)
            return f"Opened {path}."
        return f"File not found: {path}"

    def create_folder(self, params):
        path = params["path"]
        os.makedirs(path, exist_ok=True)
        return f"Created folder at {path}."

    def create_file(self, params):
        path = params["path"]
        content = params.get("content", "")
        with open(path, "w") as f:
            f.write(content)
        return f"Created file at {path}."

    def read_file(self, params):
        path = params["path"]
        if not os.path.exists(path):
            return f"File not found: {path}"
        with open(path, "r") as f:
            content = f.read()
        return content

    def list_dir(self, params):
        path = params.get("path", ".")
        if not os.path.exists(path):
            return f"Directory not found: {path}"
        items = os.listdir(path)
        return f"Contents of {path}:\n" + "\n".join(items)

    def delete_file(self, params):
        path = params["path"]
        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted {path}."
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
            return f"Deleted directory {path}."
        return f"Path not found: {path}"

    def run_command(self, params):
        cmd = params["command"]
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr
        return f"Command output:\n{output[:1000]}"

    def code_task(self, params):
        path = params.get("path", "output.py")
        description = params.get("description", "Generated code")
        language = params.get("language", "python")
        
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        
        code_snippets = {
            "python": f"# {description}\n\nif __name__ == '__main__':\n    print('Hello World')\n",
            "javascript": f"// {description}\n\nconsole.log('Hello World');\n",
            "html": f"<!DOCTYPE html>\n<html>\n<head><title>{description}</title></head>\n<body><h1>{description}</h1></body>\n</html>",
        }
        
        code = code_snippets.get(language, f"# {description}\n")
        with open(path, "w") as f:
            f.write(code)
        return f"Created {language} file at {path}."

    def read_clipboard(self, params):
        text = pyperclip.paste()
        if not text:
            return "Sir, your clipboard appears to be empty."
        return f"Clipboard content: {text[:500]}..."

    def write_clipboard(self, params):
        text = params.get("text", "")
        pyperclip.copy(text)
        return "I have updated your clipboard, Sir."
