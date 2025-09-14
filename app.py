from flask import Flask, render_template, jsonify
import subprocess
import signal
import os

app = Flask(__name__)

gesture_process = None  # To track demo.py process


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start")
def start():
    global gesture_process
    if gesture_process is None:
        gesture_process = subprocess.Popen(
            [r"C:\Users\user\gestura\.venv\Scripts\python.exe", "demo.py"]
        )
    return jsonify({"status": "Running"})


@app.route("/stop", methods=["GET", "POST"])
def stop():
    global gesture_process
    if gesture_process:
        os.kill(gesture_process.pid, signal.SIGTERM)
        gesture_process = None
    return jsonify({"status": "Stopped"})


@app.route("/status")
def status():
    return jsonify({"status": "Running" if gesture_process else "Stopped"})


if __name__ == "__main__":
    app.run(debug=True)
