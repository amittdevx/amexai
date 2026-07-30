from flask import Flask
import threading
import subprocess

app = Flask(__name__)


@app.route("/")
def home():
    return "Amex Agent is Running ✅"


# Flask run thread
def run_flask():
    app.run(host="0.0.0.0", port=8080)


# Agent run thread
def run_agent():
    subprocess.run(["python", "agent.py", "start"])


# Threads
threading.Thread(target=run_flask).start()
threading.Thread(target=run_agent).start()
