
from flask import Flask, request, jsonify, send_from_directory
import os
import shutil

app = Flask(__name__)
base_dir = os.path.abspath("vfs")
os.makedirs(base_dir, exist_ok=True)
current_dir = base_dir

@app.route("/")
def home():
    return send_from_directory(".", "terminal.html")

@app.route("/run", methods=["POST"])
def run():
    global current_dir
    command = request.json.get("command", "")
    parts = command.strip().split()
    if not parts:
        return ""

    cmd = parts[0]
    args = parts[1:]

    try:
        if cmd == "touch":
            if args:
                open(os.path.join(current_dir, args[0]), 'a').close()
                return f"File '{args[0]}' created."
        elif cmd == "mkdir":
            if args:
                os.makedirs(os.path.join(current_dir, args[0]), exist_ok=True)
                return f"Directory '{args[0]}' created."
        elif cmd == "cd":
            if args:
                new_path = os.path.abspath(os.path.join(current_dir, args[0]))
                if new_path.startswith(base_dir) and os.path.isdir(new_path):
                    current_dir = new_path
                    return f"Changed directory to '{args[0]}'"
                return "Access denied or not a directory."
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
            return "Available commands: touch, cd, mkdir, echo, pwd, rmdir, cp, cat, whoami"
        else:
            return f"Command not found: {cmd}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
