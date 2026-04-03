from flask import Flask, jsonify, render_template
from fake_data import get_fake_overlay_state

app = Flask(__name__)

# Replace this later with real shared state from listener/parser
CURRENT_STATE = get_fake_overlay_state()

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
    app.run(host="0.0.0.0", port=5000, debug=True)