from flask import Flask, request, jsonify, render_template
from yt_dlp import YoutubeDL
import threading
import os

app = Flask(__name__)
progress_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    progress_data.update({
        "status": "starting",
        "percent": 0,
        "speed": 0,
        "eta": 0,
        "complete": False
    })

    def progress_hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            downloaded = d.get("downloaded_bytes", 0)
            percent = downloaded / total * 100
            progress_data.update({
                "status": "downloading",
                "percent": percent,
                "speed": d.get("speed", 0),
                "eta": d.get("eta", 0),
            })
        elif d["status"] == "finished":
            progress_data.update({
                "status": "finished",
                "percent": 100,
                "complete": True,
                "eta": 0,
                "speed": 0
            })

    def download_video():
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'quiet': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            progress_data.update({
                "status": "error",
                "message": str(e)
            })
            print(f"Error: {e}")

    threading.Thread(target=download_video).start()
    return jsonify({"status": "Download started"})

@app.route("/status")
def status():
    return jsonify(progress_data)

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    app.run(debug=True)
