from flask import Flask, jsonify, render_template
import threading
from listener import start_listener

app = Flask(__name__)

# Starts empty and is populated by the live listener thread.
CURRENT_STATE = {}
_LISTENER_THREAD = None
_LISTENER_LOCK = threading.Lock()


def start_background_listener():
    global _LISTENER_THREAD
    with _LISTENER_LOCK:
        if _LISTENER_THREAD and _LISTENER_THREAD.is_alive():
            return

        _LISTENER_THREAD = threading.Thread(target=start_listener, args=(CURRENT_STATE,))
        _LISTENER_THREAD.daemon = True
        _LISTENER_THREAD.start()


@app.before_request
def ensure_listener_running():
    start_background_listener()


@app.route("/api/state")
def api_state():
    return jsonify(CURRENT_STATE)


@app.route("/overlay")
def overlay():
    return render_template("overlay.html")


@app.route("/debug/raw")
def debug_raw():
    return jsonify(
        {
            "listener_alive": bool(_LISTENER_THREAD and _LISTENER_THREAD.is_alive()),
            "last_packet": CURRENT_STATE.get("last_packet"),
            "listener_status": CURRENT_STATE.get("listener_status", "starting"),
            "listener_error": CURRENT_STATE.get("listener_error"),
        }
    )


if __name__ == "__main__":
    start_background_listener()
    app.run(host="0.0.0.0", port=5000, debug=True)
