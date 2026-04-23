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
    """
    닉네임을 세션에 저장합니다.
    클라이언트에서 최초 1회 호출하거나 닉네임 변경 시 호출합니다.
    """
    data = request.get_json(silent=True)
    if not data or not data.get("username", "").strip():
        return jsonify(success=False, error="유효하지 않은 닉네임입니다."), 400

    username = str(escape(data["username"].strip()))[:20]  # XSS 방지 + 20자 제한
    session["username"] = username
    return jsonify(success=True, username=username)


@app.route("/send", methods=["POST"])
def send_message():
    """
    메시지를 전송합니다.
    세션에 닉네임이 없으면 거부합니다.
    """
    if "username" not in session:
        return jsonify(success=False, error="닉네임을 먼저 설정해주세요."), 401

    data = request.get_json(silent=True)
    if not data or not data.get("message", "").strip():
        return jsonify(success=False, error="메시지가 비어있습니다."), 400

    text = str(escape(data["message"].strip()))[:500]  # XSS 방지 + 500자 제한

    message = {
        "username": session["username"],
        "text": text,
        "timestamp": datetime.utcnow().strftime("%H:%M"),  # UTC 기준 시각
    }

    messages.append(message)

    # 상한선 초과 시 오래된 메시지부터 제거
    if len(messages) > MAX_MESSAGES:
        del messages[: len(messages) - MAX_MESSAGES]

    return jsonify(success=True, message=message)


@app.route("/messages", methods=["GET"])
def get_messages():
    """
    저장된 전체 메시지를 반환합니다.
    'after' 쿼리 파라미터로 인덱스를 지정하면 그 이후 메시지만 반환합니다.
    (폴링 트래픽 절감용)
    """
    after = request.args.get("after", type=int, default=0)
    sliced = messages[after:]
    return jsonify(
        messages=sliced,
        total=len(messages),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")