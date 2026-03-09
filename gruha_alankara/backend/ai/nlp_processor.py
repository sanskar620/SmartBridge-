"""
Gruha Alankara — NLP Processor
Parses natural language commands into structured intents.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Furniture keywords used across multiple patterns
_FURNITURE_WORDS = r"(?:furniture|sofa|couch|table|lamp|chair|shelf|bookshelf|armchair|credenza|light|cushion|bed|desk)"

# Intent patterns — ORDER MATTERS: checked top to bottom.
# "recommend" is checked BEFORE "book" so advisory queries aren't mistaken for bookings.
INTENT_PATTERNS = {
    "greeting": [
        r"^(?:hi|hello|hey|namaste|namaskar|namasthe)\b",
    ],
    "analyze_room": [
        r"(?:analyze|scan|check|examine)\s+(?:my\s+)?(?:room|space|image)",
        r"(?:room|space)\s+(?:analyze|analysis|scan)",
    ],
    "recommend_furniture": [
        # Explicit recommendation verbs
        r"(?:suggest|recommend|show|find|get)\s+.*" + _FURNITURE_WORDS,
        r"(?:modern|minimalist|scandinavian|traditional|japanese|industrial)\s+" + _FURNITURE_WORDS,
        r"" + _FURNITURE_WORDS + r"\s+(?:recommend|suggest|show)",
        # Advisory / shopping queries ("tell me best sofa", "cheapest table", "which sofa to buy")
        r"(?:tell|which|what|best|cheapest|affordable|good|nice|decent|descent).*" + _FURNITURE_WORDS,
        r"" + _FURNITURE_WORDS + r".*(?:to\s+buy|to\s+get|to\s+purchase|for\s+me)",
        r"(?:i\s+need|i\s+want|looking\s+for|need)\s+(?:a\s+)?(?:new\s+)?" + _FURNITURE_WORDS,
        # Hindi
        r"(?:furniture|sofa|table)\s+(?:dikhao|batao|suggest\s+karo)",
        r"(?:dikhao|batao).*(?:furniture|sofa|table)",
        # Telugu
        r"(?:furniture|sofa|table)\s+(?:chupinchu|suggest\s+cheyyi)",
    ],
    "book_furniture": [
        # Only match explicit booking intent with a clear product target
        r"(?:book|order|reserve)\s+(?:the\s+)?(?:a\s+)?(.+)",
        r"(?:i'?d\s+like\s+to\s+book)\s+(?:the\s+)?(?:a\s+)?(.+)",
        r"(?:purchase|buy)\s+(?:the\s+)(.+)",
        # Hindi
        r"(?:book\s+karo|order\s+karo|kharido)\s+(.+)",
        # Telugu
        r"(?:book\s+cheyyi|order\s+cheyyi)\s+(.+)",
    ],
    "style_info": [
        r"(?:what|which)\s+(?:style|design|theme)",
        r"(?:tell|explain).*(?:style|design|theme)",
        r"(?:trend|trending|popular|latest)\s+(?:style|design)?",
    ],
    "budget_estimate": [
        r"(?:budget|cost|price|estimate|how\s+much)",
        r"(?:kitna|kharcha|price\s+kya)",
        r"(?:entha|dhara|price\s+entha)",
    ],
    "layout_help": [
        r"(?:layout|plan|arrange|organize)\s+(?:my\s+)?(?:room|space|living|bedroom)?",
        r"(?:room|space)\s+(?:layout|plan|arrangement)",
    ],
    "add_to_design": [
        r"(?:add|place|put|include)\s+(?:a\s+)?(.+?)(?:\s+to\s+design|\s+in\s+room)?$",
    ],
}


class NLPProcessor:
    """Parses user text into structured command intents."""

    def parse(self, text: str) -> dict:
        """
        Parse text and return intent + extracted entities.

        Returns
        -------
        dict with 'intent', 'entities', 'original_text', 'language'.
        """
        text_lower = text.strip().lower()
        language = self._detect_language(text_lower)

        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities = {}
                    if match.groups():
                        raw_target = match.group(1).strip() if match.group(1) else ""
                        entities["target"] = self._clean_target(raw_target)
                    # Extract style if mentioned
                    style = self._extract_style(text_lower)
                    if style:
                        entities["style"] = style
                    # Extract product type
                    product_type = self._extract_product_type(text_lower)
                    if product_type:
                        entities["product_type"] = product_type

                    return {
                        "intent": intent,
                        "entities": entities,
                        "original_text": text,
                        "language": language,
                        "confidence": 0.85,
                    }

        # Default / fallback
        return {
            "intent": "general_query",
            "entities": {},
            "original_text": text,
            "language": language,
            "confidence": 0.4,
        }

    @staticmethod
    def _clean_target(target: str) -> str:
        """Remove trailing questions, filler phrases, and punctuation from captured target."""
        # Strip trailing sentences starting with common question/filler words
        target = re.split(r"[.!?]\s*(?:what|how|when|where|why|can|could|shall|will|is|do|please|tell)", target)[0]
        # Remove trailing punctuation and whitespace
        target = re.sub(r"[.!?,;:\s]+$", "", target)
        # Remove leading filler like "the", "a", "an" (if that's ALL that remains)
        target = target.strip()
        return target

    @staticmethod
    def _detect_language(text: str) -> str:
        hindi_markers = ["karo", "dikhao", "batao", "kharido", "kya", "hai", "kitna", "kharcha"]
        telugu_markers = ["cheyyi", "chupinchu", "entha", "dhara", "kavali", "cheppandi"]
        for marker in hindi_markers:
            if marker in text:
                return "hi"
        for marker in telugu_markers:
            if marker in text:
                return "te"
        return "en"

    @staticmethod
    def _extract_style(text: str) -> str | None:
        styles = ["modern", "minimalist", "traditional", "scandinavian", "industrial", "japanese", "bohemian"]
        for s in styles:
            if s in text:
                return s.capitalize()
        return None

    @staticmethod
    def _extract_product_type(text: str) -> str | None:
        types = {
            "sofa": "seating", "couch": "seating", "chair": "seating", "armchair": "seating",
            "table": "tables", "coffee table": "tables", "desk": "tables",
            "lamp": "lighting", "light": "lighting", "pendant": "lighting",
            "shelf": "storage", "bookshelf": "storage", "credenza": "storage",
        }
        for keyword, category in types.items():
            if keyword in text:
                return category
        return None
