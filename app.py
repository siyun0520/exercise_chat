import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from markupsafe import escape

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-this")

messages = []
MAX_MESSAGES = 200  # 메모리 과부하 방지용 상한선


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/set_username", methods=["POST"])
def set_username():

    data = request.get_json(silent=True)
    if not data or not data.get("username", "").strip():
        return jsonify(success=False, error="Unvalid name"), 400

    username = str(escape(data["username"].strip()))[:20]  # XSS 방지 + 20자 제한
    session["username"] = username
    return jsonify(success=True, username=username)


@app.route("/send", methods=["POST"])
def send_message():

    if "username" not in session:
        return jsonify(success=False, error="Set your name first"), 401

    data = request.get_json(silent=True)
    if not data or not data.get("message", "").strip():
        return jsonify(success=False, error="You can't post an empty message"), 400

    text = str(escape(data["message"].strip()))[:500]  # XSS 방지 + 500자 제한

    message = {
        "username": session["username"],
        "text": text,
        "timestamp": datetime.utcnow().strftime("%H:%M"),  # UTC 기준 시각
    }

    messages.append(message)

    if len(messages) > MAX_MESSAGES:
        del messages[: len(messages) - MAX_MESSAGES]

    return jsonify(success=True, message=message)


@app.route("/messages", methods=["GET"])
def get_messages():

    after = request.args.get("after", type=int, default=0)
    sliced = messages[after:]
    return jsonify(
        messages=sliced,
        total=len(messages),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")