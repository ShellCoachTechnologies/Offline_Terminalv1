
from flask import Flask, request, send_from_directory
import os
import shutil
import time

app = Flask(__name__)
base_dir = os.path.abspath("vfs")
os.makedirs(base_dir, exist_ok=True)
current_dir = base_dir

@app.route("/")
def index():
    return send_from_directory(".", "terminal.html")

@app.route("/run", methods=["POST"])
def run_command():
    global current_dir
    import json
    data = request.json
    command = data.get("command", "").strip()
    if not command:
        return ""
    parts = command.split()
    cmd = parts[0]
    args = parts[1:]

    try:
        if cmd == "ls":
            files = os.listdir(current_dir)
            output = []
            for f in files:
                path = os.path.join(current_dir, f)
                mode = "d" if os.path.isdir(path) else "-"
                perms = "rwxr-xr-x"
                size = os.path.getsize(path)
                timestamp = time.strftime("%b %d %H:%M", time.localtime(os.path.getmtime(path)))
                output.append(f"{mode}{perms} 1 user user {size} {timestamp} {f}")
            return "\n".join(output) or "(empty)"
        elif cmd == "mkdir":
            if args:
                os.makedirs(os.path.join(current_dir, args[0]), exist_ok=True)
                return f"Directory '{args[0]}' created."
        elif cmd == "cd":
            if args:
                target = os.path.abspath(os.path.join(current_dir, args[0]))
                if target.startswith(base_dir) and os.path.isdir(target):
                    current_dir = target
                    return f"Changed directory to {args[0]}"
                return "Directory not found."
        elif cmd == "touch":
            if args:
                open(os.path.join(current_dir, args[0]), "a").close()
                return f"File '{args[0]}' created."
        elif cmd == "pwd":
            return current_dir.replace(base_dir, "/")
        elif cmd == "echo":
            return " ".join(args)
        elif cmd == "rmdir":
            if args:
                os.rmdir(os.path.join(current_dir, args[0]))
                return f"Directory '{args[0]}' removed."
        elif cmd == "cp":
            if len(args) == 2:
                shutil.copy(os.path.join(current_dir, args[0]), os.path.join(current_dir, args[1]))
                return f"Copied '{args[0]}' to '{args[1]}'"
        elif cmd == "cat":
            if args:
                with open(os.path.join(current_dir, args[0]), "r") as f:
                    return f.read()
        elif cmd == "whoami":
            return "cloudnix_user"
        elif cmd == "help":
            return "Available: ls -l, mkdir, cd, touch, pwd, echo, rmdir, cp, cat, whoami"
        else:
            return f"Command not found: {cmd}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
