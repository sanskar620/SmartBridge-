"""
Gruha Alankara — Voice Processor
Speech-to-text and text-to-speech with multilingual support.
"""

import io
import logging
import os
import uuid
import base64

logger = logging.getLogger(__name__)

# Language code mapping
LANGUAGE_MAP = {
    "en": {"code": "en-IN", "tts": "en", "name": "English"},
    "hi": {"code": "hi-IN", "tts": "hi", "name": "Hindi"},
    "te": {"code": "te-IN", "tts": "te", "name": "Telugu"},
}


class VoiceProcessor:
    """Handles speech-to-text and text-to-speech operations."""

    def __init__(self, storage_dir: str | None = None):
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "..", "storage")
        os.makedirs(self.storage_dir, exist_ok=True)

    def speech_to_text(self, audio_data: bytes, language: str = "en") -> dict:
        """
        Convert speech audio to text.

        Parameters
        ----------
        audio_data : bytes
            Raw audio bytes (WAV format expected).
        language : str
            Language code: 'en', 'hi', or 'te'.

        Returns
        -------
        dict with 'text', 'language', 'success'.
        """
        try:
            import speech_recognition as sr
        except ImportError:
            return {"success": False, "error": "SpeechRecognition library not installed", "text": ""}

        lang_info = LANGUAGE_MAP.get(language, LANGUAGE_MAP["en"])
        recognizer = sr.Recognizer()

        try:
            audio_file = io.BytesIO(audio_data)
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)

            text = recognizer.recognize_google(audio, language=lang_info["code"])
            return {
                "success": True,
                "text": text,
                "language": lang_info["name"],
                "language_code": language,
            }
        except sr.UnknownValueError:
            return {"success": False, "text": "", "error": "Could not understand the audio"}
        except sr.RequestError as e:
            return {"success": False, "text": "", "error": f"Speech recognition service error: {e}"}
        except Exception as e:
            logger.exception("Speech-to-text error")
            return {"success": False, "text": "", "error": str(e)}

    def text_to_speech(self, text: str, language: str = "en") -> dict:
        """
        Convert text to speech audio (base64-encoded MP3).

        Parameters
        ----------
        text : str
            The text to speak.
        language : str
            Language code: 'en', 'hi', or 'te'.

        Returns
        -------
        dict with 'audio_base64', 'language', 'success'.
        """
        try:
            from gtts import gTTS
        except ImportError:
            return {"success": False, "error": "gTTS library not installed"}

        lang_info = LANGUAGE_MAP.get(language, LANGUAGE_MAP["en"])

        try:
            tts = gTTS(text=text, lang=lang_info["tts"])
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            audio_b64 = base64.b64encode(buffer.read()).decode("utf-8")

            return {
                "success": True,
                "audio_base64": audio_b64,
                "content_type": "audio/mpeg",
                "language": lang_info["name"],
            }
        except Exception as e:
            logger.exception("Text-to-speech error")
            return {"success": False, "error": str(e)}

    def get_supported_languages(self) -> list[dict]:
        """Return list of supported languages."""
        return [{"code": k, **v} for k, v in LANGUAGE_MAP.items()]
