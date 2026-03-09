"""
Gruha Alankara — Voice & Chat Routes
Handles Buddy AI chat and voice command endpoints.
"""

import logging

from flask import Blueprint, request, jsonify

from ai.buddy_agent import BuddyAgent
from ai.voice_processor import VoiceProcessor

logger = logging.getLogger(__name__)

voice_bp = Blueprint("voice", __name__)

# Singletons initialised on first request
_buddy: BuddyAgent | None = None
_voice: VoiceProcessor | None = None


def _get_buddy() -> BuddyAgent:
    global _buddy
    if _buddy is None:
        _buddy = BuddyAgent()
    return _buddy


def _get_voice() -> VoiceProcessor:
    global _voice
    if _voice is None:
        _voice = VoiceProcessor()
    return _voice


@voice_bp.route("/chat", methods=["POST"])
def chat():
    """Send a text message to Buddy and get a response."""
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"success": False, "error": "Missing 'message' in request body"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"success": False, "error": "Empty message"}), 400

    user_id = data.get("user_id")
    buddy = _get_buddy()
    result = buddy.chat(user_message, user_id)

    return jsonify({
        "success": True,
        "response": result["response"],
        "intent": result["intent"],
        "data": result.get("data"),
        "language": result["language"],
    })


@voice_bp.route("/voice-command", methods=["POST"])
def voice_command():
    """Process a voice command: audio → text → Buddy → response + optional TTS."""
    voice = _get_voice()

    # Accept either audio file upload or pre-transcribed text
    if "audio" in request.files:
        audio_file = request.files["audio"]
        language = request.form.get("language", "en")
        audio_bytes = audio_file.read()
        stt_result = voice.speech_to_text(audio_bytes, language)

        if not stt_result["success"]:
            return jsonify({"success": False, "error": stt_result["error"]}), 400

        transcribed_text = stt_result["text"]
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        transcribed_text = data.get("text", "")
        language = data.get("language", "en")
        if not transcribed_text:
            return jsonify({"success": False, "error": "No audio or text provided"}), 400
    else:
        return jsonify({"success": False, "error": "Send audio file or JSON with 'text'"}), 400

    # Process through Buddy
    buddy = _get_buddy()
    user_id = request.form.get("user_id") or (request.get_json(silent=True) or {}).get("user_id")
    chat_result = buddy.chat(transcribed_text, user_id)

    # Generate TTS response
    tts_result = voice.text_to_speech(chat_result["response"], language)

    return jsonify({
        "success": True,
        "transcribed_text": transcribed_text,
        "response": chat_result["response"],
        "intent": chat_result["intent"],
        "audio": tts_result if tts_result.get("success") else None,
        "language": language,
    })


@voice_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech audio."""
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"success": False, "error": "Missing 'text'"}), 400

    language = data.get("language", "en")
    voice = _get_voice()
    result = voice.text_to_speech(data["text"], language)

    if not result["success"]:
        return jsonify(result), 500

    return jsonify({"success": True, **result})


@voice_bp.route("/supported-languages", methods=["GET"])
def supported_languages():
    """Return list of supported voice languages."""
    voice = _get_voice()
    return jsonify({
        "success": True,
        "languages": voice.get_supported_languages(),
    })
