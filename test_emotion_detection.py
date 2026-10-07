"""Tests for the emotion detection module."""

import pytest

from EmotionDetection import emotion_detector, format_emotion


def test_emotion_detector_returns_a_complete_result():
    result = emotion_detector("I am very happy and excited today.")

    assert set(result).issuperset({
        "anger",
        "disgust",
        "fear",
        "joy",
        "sadness",
        "dominant_emotion",
        "dominant_score",
    })
    assert result["dominant_emotion"] in {"anger", "disgust", "fear", "joy", "sadness"}
    assert 0 <= result["dominant_score"] <= 100


def test_emotion_detector_rejects_blank_text():
    with pytest.raises(ValueError, match="Text is blank"):
        emotion_detector("   ")


def test_format_emotion_displays_the_summary():
    payload = {
        "anger": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "joy": 100.0,
        "sadness": 0.0,
        "dominant_emotion": "joy",
        "dominant_score": 100.0,
    }

    message = format_emotion(payload)
    assert "joy" in message.lower()
    assert "dominant" in message.lower()
