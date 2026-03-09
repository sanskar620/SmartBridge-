"""
Gruha Alankara — Furniture Search / Recommendation Service
Returns furniture recommendations based on room size and detected style.
"""

import logging
from models.product_model import Product

logger = logging.getLogger(__name__)

# Mapping of styles → compatible product styles
STYLE_COMPAT = {
    "Modern": ["Modern", "Minimalist", "Contemporary", "Luxe Minimal"],
    "Minimalist": ["Minimalist", "Scandinavian", "Modern", "Japanese"],
    "Traditional": ["Traditional", "Wabi-Sabi"],
    "Scandinavian": ["Scandinavian", "Minimalist", "Modern"],
    "Industrial": ["Industrial", "Modern"],
    "Japanese": ["Japanese", "Minimalist", "Wabi-Sabi"],
    "Bohemian": ["Contemporary", "Traditional", "Wabi-Sabi"],
}

# Recommended categories based on room size
SIZE_CATEGORIES = {
    "small": ["seating", "lighting", "tables"],
    "medium": ["seating", "tables", "lighting", "storage"],
    "large": ["seating", "tables", "lighting", "storage"],
}


class FurnitureSearchService:
    """Recommends furniture products from the catalog."""

    def recommend(self, style: str, room_area: float = 15.0) -> list[dict]:
        """
        Return product recommendations for the given style and room area.

        Parameters
        ----------
        style : str
            Primary detected design style.
        room_area : float
            Estimated room area in m².

        Returns
        -------
        List of product dicts sorted by relevance.
        """
        size_class = self._classify_room_size(room_area)
        compatible_styles = STYLE_COMPAT.get(style, list(STYLE_COMPAT.get("Modern", [])))
        allowed_categories = SIZE_CATEGORIES.get(size_class, SIZE_CATEGORIES["medium"])

        # Query products matching compatible styles
        products = Product.query.filter(
            Product.style.in_(compatible_styles)
        ).all()

        # If not enough products, include all
        if len(products) < 3:
            products = Product.query.all()

        # Score and sort
        scored = []
        for p in products:
            score = 0
            if p.style in compatible_styles:
                score += 3
            if p.category in allowed_categories:
                score += 2
            if size_class == "small" and p.price < 30000:
                score += 1
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item.to_dict() for _, item in scored[:8]]

    def search_by_name(self, query: str) -> list[dict]:
        """Search products by name (case-insensitive partial match)."""
        results = Product.query.filter(
            Product.product_name.ilike(f"%{query}%")
        ).all()
        return [p.to_dict() for p in results]

    def search_by_category(self, category: str) -> list[dict]:
        """Search products by category."""
        results = Product.query.filter_by(category=category).all()
        return [p.to_dict() for p in results]

    def get_all_products(self) -> list[dict]:
        """Return every product in the catalog."""
        return [p.to_dict() for p in Product.query.all()]

    @staticmethod
    def _classify_room_size(area: float) -> str:
        if area < 12:
            return "small"
        if area < 25:
            return "medium"
        return "large"
