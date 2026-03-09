"""
Gruha Alankara — Buddy AI Agent
LangChain-powered autonomous agent for interior design assistance.
"""

import logging
from typing import Any

from ai.nlp_processor import NLPProcessor
from services.furniture_search import FurnitureSearchService
from services.booking_agent import BookingAgentService

logger = logging.getLogger(__name__)

# ---- Pre-built knowledge base for Buddy responses ----

STYLE_KNOWLEDGE = {
    "Modern": "Modern interior design emphasizes clean lines, neutral palettes, and functional elegance. Key materials include glass, metal, and polished surfaces.",
    "Minimalist": "Minimalist design follows the 'less is more' philosophy — open spaces, limited furniture, purposeful decor, and a palette of whites and earth tones.",
    "Traditional": "Traditional style features rich textures, warm colors, ornate details, and classic furniture shapes. Think mahogany, velvet, and layered accessories.",
    "Scandinavian": "Scandinavian design is all about hygge — warmth, natural light, pale woods, textiles, and a soft, neutral color palette.",
    "Industrial": "Industrial design celebrates raw, exposed materials like brick, metal, concrete pipes, and reclaimed wood with urban authenticity.",
    "Japanese": "Japanese interior design embraces wabi-sabi — beauty in imperfection, natural materials, negative space, and zen-like serenity.",
    "Bohemian": "Bohemian style is free-spirited, layered, and eclectic — rich patterns, global textiles, plants, and curated collections.",
}

BUDGET_ESTIMATES = {
    "living room": {"low": "₹1,20,000", "mid": "₹2,50,000", "high": "₹5,00,000+"},
    "bedroom": {"low": "₹80,000", "mid": "₹1,80,000", "high": "₹3,50,000+"},
    "kitchen": {"low": "₹1,50,000", "mid": "₹3,00,000", "high": "₹6,00,000+"},
    "office": {"low": "₹60,000", "mid": "₹1,50,000", "high": "₹3,00,000+"},
}

DESIGN_TRENDS = [
    "Japandi minimalism with warm neutrals",
    "Biophilic design — bringing nature indoors",
    "Curved furniture replacing sharp geometric edges",
    "Quiet luxury — understated, premium materials",
    "Multifunctional furniture for compact living",
    "Earth tones and terracotta accents",
    "Sustainable and upcycled furnishings",
]


class BuddyAgent:
    """
    Buddy — the AI interior design assistant.
    Uses NLP to parse user intent and performs actions like recommending
    furniture, providing style advice, and automating bookings.
    """

    def __init__(self):
        self.nlp = NLPProcessor()
        self.furniture_service = FurnitureSearchService()
        self.booking_service = BookingAgentService()

    def chat(self, user_message: str, user_id: int | None = None) -> dict:
        """
        Process a user message and return Buddy's response.

        Parameters
        ----------
        user_message : str
            The user's chat message or voice-transcribed text.
        user_id : int | None
            Optional user id for booking context.

        Returns
        -------
        dict with 'response', 'intent', 'data', 'language'.
        """
        parsed = self.nlp.parse(user_message)
        intent = parsed["intent"]
        entities = parsed["entities"]
        language = parsed["language"]

        handler = self._get_handler(intent)
        result = handler(entities, user_id)

        return {
            "response": result["text"],
            "intent": intent,
            "data": result.get("data"),
            "language": language,
        }

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    def _get_handler(self, intent: str):
        handlers = {
            "recommend_furniture": self._handle_recommend,
            "book_furniture": self._handle_book,
            "analyze_room": self._handle_analyze,
            "style_info": self._handle_style_info,
            "budget_estimate": self._handle_budget,
            "layout_help": self._handle_layout,
            "greeting": self._handle_greeting,
            "add_to_design": self._handle_add_to_design,
            "general_query": self._handle_general,
        }
        return handlers.get(intent, self._handle_general)

    def _handle_recommend(self, entities: dict, user_id: Any) -> dict:
        style = entities.get("style", "Modern")
        products = self.furniture_service.recommend(style)
        if not products:
            return {"text": f"I couldn't find furniture for {style} style right now. Let me suggest trying 'Modern' or 'Scandinavian' styles."}

        product_lines = []
        for p in products[:5]:
            product_lines.append(f"• {p['product_name']} ({p['style']}) — ₹{p['price']:,.0f}")
        product_list = "\n".join(product_lines)

        text = (
            f"Here are my top {style} furniture recommendations:\n\n"
            f"{product_list}\n\n"
            f"Would you like to book any of these, or shall I suggest a different style?"
        )
        return {"text": text, "data": {"products": products[:5]}}

    def _handle_book(self, entities: dict, user_id: Any) -> dict:
        target = entities.get("target", "")
        if not target:
            return {"text": "Which product would you like to book? Please specify the furniture name."}

        result = self.booking_service.book_by_name(target, user_id)
        if result["success"]:
            return {
                "text": (
                    f"✅ {result['message']}\n\n"
                    f"Booking ID: #{result['booking_id']}\n"
                    f"Status: {result['status'].capitalize()}\n"
                    f"Date: {result['booking_date'][:10]}\n\n"
                    f"Your furniture will be reserved. Is there anything else I can help with?"
                ),
                "data": result,
            }

        # Booking target not found — try to recommend instead of just failing
        style = entities.get("style", "Modern")
        products = self.furniture_service.recommend(style)
        if products:
            product_lines = [f"• {p['product_name']} ({p['style']}) — ₹{p['price']:,.0f}" for p in products[:5]]
            return {
                "text": (
                    f"I couldn't find '{target}' in our catalog. "
                    f"Here are some items you can book:\n\n"
                    + "\n".join(product_lines)
                    + "\n\nJust say 'Book the <name>' to reserve one!"
                ),
                "data": {"products": products[:5]},
            }
        return {"text": f"I couldn't find '{target}' in our catalog. Try asking me to 'show furniture' to see what's available."}

    def _handle_analyze(self, entities: dict, user_id: Any) -> dict:
        return {
            "text": (
                "To analyze your room, please upload a room image using the Upload section above. "
                "Once uploaded, click 'Analyze Room' and I'll provide:\n\n"
                "• Style detection\n• Lighting quality assessment\n"
                "• Space utilization score\n• Color palette analysis\n\n"
                "Go ahead and upload your room photo!"
            )
        }

    def _handle_style_info(self, entities: dict, user_id: Any) -> dict:
        style = entities.get("style")
        if style and style in STYLE_KNOWLEDGE:
            return {
                "text": f"🎨 **{style} Style**\n\n{STYLE_KNOWLEDGE[style]}\n\nWould you like furniture recommendations for this style?"
            }
        # Return trends
        trends = "\n".join(f"• {t}" for t in DESIGN_TRENDS)
        return {
            "text": f"🎨 Top Interior Design Trends:\n\n{trends}\n\nWhich style resonates with you? I can recommend furniture to match."
        }

    def _handle_budget(self, entities: dict, user_id: Any) -> dict:
        text_lines = ["💰 Budget Estimates by Room Type:\n"]
        for room, prices in BUDGET_ESTIMATES.items():
            text_lines.append(f"**{room.title()}**")
            text_lines.append(f"  Budget: {prices['low']} | Mid: {prices['mid']} | Premium: {prices['high']}")
        text_lines.append("\nThese are approximate ranges. I can help optimize within your specific budget!")
        return {"text": "\n".join(text_lines)}

    def _handle_layout(self, entities: dict, user_id: Any) -> dict:
        return {
            "text": (
                "📐 Room Layout Planning Tips:\n\n"
                "1. Define clear zones — seating, dining, workspace\n"
                "2. Maintain 90cm walkways between furniture\n"
                "3. Anchor with a large area rug (at least 2/3 of seating area)\n"
                "4. Face seating toward the focal point (TV, window, fireplace)\n"
                "5. Use vertical space — shelves and wall-mounted storage\n"
                "6. Layer lighting at 3 levels: ambient, task, accent\n\n"
                "Upload a room image and I'll generate a personalized layout plan!"
            )
        }

    def _handle_greeting(self, entities: dict, user_id: Any) -> dict:
        return {
            "text": (
                "Hello! I'm Buddy, your AI interior design assistant. 🏠\n\n"
                "I can help you with:\n"
                "• Furniture recommendations\n"
                "• Style analysis and suggestions\n"
                "• Budget planning\n"
                "• Room layout advice\n"
                "• Automated furniture booking\n\n"
                "What would you like to explore today?"
            )
        }

    def _handle_add_to_design(self, entities: dict, user_id: Any) -> dict:
        target = entities.get("target", "furniture piece")
        return {
            "text": (
                f"I've noted your request to add '{target}' to the design. "
                f"Head to the AR Designer section to preview it in your space, "
                f"or I can search our catalog for matching products. Shall I search?"
            )
        }

    def _handle_general(self, entities: dict, user_id: Any) -> dict:
        # If the message mentions any furniture keyword, try to recommend
        original = entities.get("original_text", "")
        style = entities.get("style", "Modern")
        furniture_keywords = ["sofa", "couch", "table", "lamp", "chair", "shelf", "bookshelf",
                              "furniture", "armchair", "credenza", "light", "cushion", "bed", "desk"]
        if any(kw in (original or "").lower() for kw in furniture_keywords):
            products = self.furniture_service.recommend(style)
            if products:
                product_lines = [f"• {p['product_name']} ({p['style']}) — ₹{p['price']:,.0f}" for p in products[:5]]
                return {
                    "text": (
                        f"Here are some {style} furniture recommendations for you:\n\n"
                        + "\n".join(product_lines)
                        + "\n\nWould you like to book any of these, or want a different style?"
                    ),
                    "data": {"products": products[:5]},
                }

        return {
            "text": (
                "Great question! I'm here to help with interior design. I can:\n\n"
                "• Recommend furniture for your style\n"
                "• Provide budget estimates\n"
                "• Explain design trends and styles\n"
                "• Help plan room layouts\n"
                "• Book furniture autonomously\n\n"
                "Try asking something like 'Suggest modern furniture' or 'Book the Oslo Sofa'."
            )
        }
