from flask import Flask, jsonify, render_template
from fake_data import get_fake_overlay_state
import threading
from listener import start_listener

app = Flask(__name__)

# Replace this later with real shared state from listener/parser
CURRENT_STATE = {}

def start_background_listener():
    t = threading.Thread(target=start_listener, args=(CURRENT_STATE,))
    t.daemon = True
    t.start()

@app.route("/api/state")
def api_state():
    return jsonify(CURRENT_STATE)

@app.route("/overlay")
def overlay():
    return render_template("overlay.html")

@app.route("/debug/raw")
def debug_raw():
    return {
        "status": "ok",
        "message": "Raw packet debug endpoint placeholder"
    }

if __name__ == "__main__":
    start_background_listener()
    app.run(host="0.0.0.0", port=5000, debug=True)