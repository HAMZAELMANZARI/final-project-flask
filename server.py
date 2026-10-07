"""Flask web application for the emotion detector demo."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from EmotionDetection import emotion_detector, format_emotion

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    """Render the web form."""
    return render_template("index.html")


def _get_text_from_request() -> str:
    """Extract the text field from JSON or form submissions."""
    if request.method == "POST":
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            text = payload.get("text", "")
            if text:
                return str(text)
        text = request.form.get("text", "")
        if text:
            return str(text)
        text = request.form.get("textToAnalyze", "")
        return str(text)

    text = request.args.get("text", "")
    if text:
        return str(text)
    return str(request.args.get("textToAnalyze", ""))


@app.route("/emotion", methods=["GET", "POST"])
def emotion() -> object:
    """Handle form submissions and return JSON output."""
    text = _get_text_from_request()
    if not text.strip():
        return jsonify({"error": "Text is blank. Please provide a non-empty text."}), 400

    result = emotion_detector(text)
    return jsonify({
        "emotion": result,
        "formatted": format_emotion(result),
    })


@app.route("/emotionDetector", methods=["GET", "POST"])
def emotion_detector_route() -> object:
    """Compatibility route matching the legacy form JS."""
    text = _get_text_from_request()
    if not text.strip():
        return "Text is blank. Please provide a non-empty text.", 400

    result = emotion_detector(text)
    return format_emotion(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
