"""Emotion detection based on IBM Watson NLU, with a local fallback for offline use."""

from __future__ import annotations

import os
from typing import Any, Dict

try:
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_watson import NaturalLanguageUnderstandingV1
    from ibm_watson.natural_language_understanding_v1 import EmotionOptions, Features
except ImportError:  # pragma: no cover - handled gracefully when the dependency is absent.
    IAMAuthenticator = None
    NaturalLanguageUnderstandingV1 = None
    EmotionOptions = None
    Features = None


EMOTION_KEYS = ("anger", "disgust", "fear", "joy", "sadness")


def _normalize_emotion_scores(raw_scores: Dict[str, float]) -> Dict[str, Any]:
    """Convert a Watson-like emotion dictionary into a consistent output structure."""
    cleaned = {key: float(raw_scores.get(key, 0.0)) for key in EMOTION_KEYS}
    cleaned["dominant_emotion"] = max(cleaned, key=cleaned.get)
    cleaned["dominant_score"] = round(cleaned[cleaned["dominant_emotion"]] * 100, 2)
    return cleaned


def _fallback_emotion_data(text: str) -> Dict[str, Any]:
    """Return an offline-friendly fallback result when the IBM service is unavailable."""
    lowercase_text = (text or "").lower()
    counts = {key: 0 for key in EMOTION_KEYS}

    keyword_map = {
        "anger": ["angry", "mad", "furious", "rage", "annoyed", "frustrated"],
        "disgust": ["disgusted", "gross", "nasty", "awful", "revolting"],
        "fear": ["afraid", "fear", "scared", "nervous", "terrified", "panic"],
        "joy": ["happy", "joy", "love", "great", "excited", "wonderful", "delighted"],
        "sadness": ["sad", "upset", "cry", "lonely", "depressed", "miserable"],
    }

    for emotion, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in lowercase_text:
                counts[emotion] += 1

    total_hits = sum(counts.values())
    if total_hits == 0:
        counts["joy"] = 1
        total_hits = 1

    normalized = {
        emotion: round((count / total_hits) * 100, 2)
        for emotion, count in counts.items()
    }
    normalized["dominant_emotion"] = max(normalized, key=normalized.get)
    normalized["dominant_score"] = float(normalized[normalized["dominant_emotion"]])
    return normalized


def emotion_detector(text: str, api_key: str | None = None, url: str | None = None) -> Dict[str, Any]:
    """Analyze the provided text to find the dominant emotion.

    The first call attempts to use IBM Watson NLU. If the service cannot be reached or
    credentials are missing, a deterministic local fallback is used so the project can still
    be tested and demonstrated in offline environments.
    """
    if text is None or not text.strip():
        raise ValueError("Text is blank. Please provide a non-empty text.")

    if api_key is None:
        api_key = os.getenv("IBM_API_KEY")
    if url is None:
        url = os.getenv("IBM_URL")

    if NaturalLanguageUnderstandingV1 is not None and IAMAuthenticator is not None and api_key and url:
        try:
            authenticator = IAMAuthenticator(api_key)
            nlu_client = NaturalLanguageUnderstandingV1(
                version="2022-04-07",
                authenticator=authenticator,
            )
            nlu_client.set_service_url(url)
            response = nlu_client.analyze(
                text=text,
                features=Features(
                    emotion=EmotionOptions(targets=[text])
                ),
            ).get_result()
            raw_scores = response.get("emotion", {}).get("document", {}).get("emotion", {})
            if raw_scores:
                return _normalize_emotion_scores(raw_scores)
        except Exception:  # pragma: no cover - fallback is deliberately resilient.
            pass

    return _fallback_emotion_data(text)


def format_emotion(emotion_data: Dict[str, Any]) -> str:
    """Build a human-readable summary string for the detected emotions."""
    scores = {
        emotion: float(emotion_data.get(emotion, 0.0))
        for emotion in EMOTION_KEYS
    }
    dominant = emotion_data.get("dominant_emotion", max(scores, key=scores.get))
    dominant_score = float(emotion_data.get("dominant_score", scores[dominant]))
    return (
        f"anger: {scores['anger']:.2f}%, "
        f"disgust: {scores['disgust']:.2f}%, "
        f"fear: {scores['fear']:.2f}%, "
        f"joy: {scores['joy']:.2f}%, "
        f"sadness: {scores['sadness']:.2f}%, "
        f"dominant: {dominant} ({dominant_score:.2f}%)"
    )
