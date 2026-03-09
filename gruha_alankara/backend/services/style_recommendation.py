"""
Gruha Alankara — Style Recommendation Service
Predicts interior design styles from room analysis data.
"""

import logging
import random

logger = logging.getLogger(__name__)

# Style definitions with characteristic features
STYLES = {
    "Modern": {
        "keywords": ["clean", "sleek", "neutral", "open"],
        "color_hint": "neutral",
        "brightness_range": (100, 200),
        "description": "Clean lines, neutral palette, and functional elegance",
    },
    "Minimalist": {
        "keywords": ["simple", "white", "space", "light"],
        "color_hint": "light",
        "brightness_range": (140, 255),
        "description": "Less is more — open spaces with purposeful decor",
    },
    "Traditional": {
        "keywords": ["warm", "rich", "ornate", "classic"],
        "color_hint": "warm",
        "brightness_range": (50, 150),
        "description": "Timeless elegance with rich textures and patterns",
    },
    "Scandinavian": {
        "keywords": ["nordic", "wood", "cozy", "bright"],
        "color_hint": "cool-neutral",
        "brightness_range": (130, 240),
        "description": "Light, airy spaces with natural wood and hygge comforts",
    },
    "Industrial": {
        "keywords": ["raw", "metal", "exposed", "urban"],
        "color_hint": "dark",
        "brightness_range": (40, 120),
        "description": "Exposed materials, raw textures, and urban character",
    },
    "Japanese": {
        "keywords": ["zen", "simple", "natural", "calm"],
        "color_hint": "earth",
        "brightness_range": (90, 180),
        "description": "Zen-inspired harmony with natural materials and balance",
    },
    "Bohemian": {
        "keywords": ["eclectic", "colorful", "layered", "vibrant"],
        "color_hint": "colorful",
        "brightness_range": (80, 180),
        "description": "Free-spirited mix of patterns, textures, and colors",
    },
}


class StyleRecommendationService:
    """Predicts suitable interior design styles for a room."""

    def recommend(self, analysis: dict) -> dict:
        """
        Given room analysis data, return ranked style recommendations.

        Parameters
        ----------
        analysis : dict
            Output from ImageAnalysisService.analyze() containing
            brightness, dominant_colors, floor_space_pct, etc.

        Returns
        -------
        dict with 'primary_style', 'secondary_styles', and details.
        """
        scores: dict[str, float] = {}

        brightness = analysis.get("brightness", "Moderate")
        floor_space = analysis.get("floor_space_pct", 50)
        edge_density = analysis.get("edge_density", 5)
        dominant_colors = analysis.get("dominant_colors", [])

        for style_name, style_info in STYLES.items():
            score = 0.0

            # Brightness matching
            if brightness == "Bright" and style_info["brightness_range"][1] > 180:
                score += 3
            elif brightness == "Well-Lit" and style_info["brightness_range"][1] > 140:
                score += 2
            elif brightness == "Dim" and style_info["brightness_range"][0] < 80:
                score += 2

            # Floor space → Minimalist / Scandinavian if high
            if floor_space > 70:
                if style_name in ("Minimalist", "Scandinavian", "Japanese"):
                    score += 3
            elif floor_space < 40:
                if style_name in ("Traditional", "Bohemian"):
                    score += 2

            # Edge density → more edges = more objects = Traditional / Bohemian
            if edge_density > 8:
                if style_name in ("Traditional", "Bohemian", "Industrial"):
                    score += 2
            else:
                if style_name in ("Minimalist", "Modern", "Scandinavian"):
                    score += 2

            # Color palette heuristic
            if dominant_colors:
                avg_val = _average_color_brightness(dominant_colors)
                if avg_val > 180 and style_name in ("Minimalist", "Scandinavian"):
                    score += 2
                elif avg_val < 80 and style_name in ("Industrial", "Traditional"):
                    score += 2

            # Small randomness to avoid always identical results
            score += random.uniform(0, 0.5)
            scores[style_name] = round(score, 2)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = ranked[0][0]
        secondary = [s[0] for s in ranked[1:4]]

        return {
            "primary_style": primary,
            "primary_description": STYLES[primary]["description"],
            "secondary_styles": secondary,
            "confidence": min(round(ranked[0][1] / 10 * 100, 1), 98),
            "all_scores": dict(ranked),
        }


def _average_color_brightness(hex_colors: list[str]) -> float:
    """Compute average brightness from a list of hex color strings."""
    total = 0
    count = 0
    for hx in hex_colors:
        hx = hx.lstrip("#")
        if len(hx) == 6:
            r, g, b = int(hx[:2], 16), int(hx[2:4], 16), int(hx[4:], 16)
            total += (r + g + b) / 3
            count += 1
    return total / count if count else 128
