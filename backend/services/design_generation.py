"""
Gruha Alankara — Design Generation Service
Generates structured interior design plans.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

from database.db import db
from models.design_model import Design

logger = logging.getLogger(__name__)

# Color themes per style
COLOR_THEMES = {
    "Modern": {"primary": "#2C2C2C", "secondary": "#E8E8E8", "accent": "#D4A574"},
    "Minimalist": {"primary": "#FFFFFF", "secondary": "#F5F5F0", "accent": "#B8B8B0"},
    "Traditional": {"primary": "#5C3A1E", "secondary": "#E8D5B7", "accent": "#8B1A1A"},
    "Scandinavian": {"primary": "#FAFAF5", "secondary": "#D4C5A9", "accent": "#7BA098"},
    "Industrial": {"primary": "#3C3C3C", "secondary": "#8C8C8C", "accent": "#C07030"},
    "Japanese": {"primary": "#F0E8D8", "secondary": "#8C7A5C", "accent": "#5A7A5A"},
    "Bohemian": {"primary": "#E8D5B7", "secondary": "#C07030", "accent": "#5A3A7A"},
}

# Layout templates per style
LAYOUT_TEMPLATES = {
    "Modern": [
        "Center the sofa facing the feature wall",
        "Place a sleek coffee table 45cm from the sofa",
        "Add a floor lamp in the corner for ambient lighting",
        "Mount a minimalist shelf on the accent wall",
    ],
    "Minimalist": [
        "Place one statement seating in the center",
        "Keep a single low-profile table nearby",
        "Use a single pendant light overhead",
        "Leave 60% of floor space empty for openness",
    ],
    "Traditional": [
        "Arrange seating around a focal point (fireplace or window)",
        "Add a classic coffee table at the center",
        "Layer with table lamps on side tables",
        "Display a bookshelf along one full wall",
    ],
    "Scandinavian": [
        "Position seating to maximize natural light",
        "Use a wooden coffee table with organic shape",
        "Add a cozy floor lamp with warm bulb",
        "Include open shelving with curated accessories",
    ],
    "Industrial": [
        "Pair a leather sofa against an exposed wall",
        "Use a metal-and-wood coffee table",
        "Add an adjustable floor lamp",
        "Include open metal shelving for storage",
    ],
    "Japanese": [
        "Use low-height seating close to the floor",
        "Place a simple wooden low table centrally",
        "Use paper lantern or soft pendant light",
        "Keep surfaces clear — embrace negative space",
    ],
    "Bohemian": [
        "Layer seating with cushions and throws",
        "Place an eclectic coffee table with character",
        "Use string lights and multiple candle holders",
        "Stack books and plant pots across shelves",
    ],
}


class DesignGenerationService:
    """Generates complete design plans and persists them."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(
        self,
        room_image_path: str,
        style: str,
        furniture: list[dict],
        analysis: dict,
        user_id: int | None = None,
    ) -> dict:
        """
        Generate a structured design plan.

        Returns
        -------
        dict containing layout suggestions, color theme, furniture placements,
        and the saved design record id.
        """
        style_key = style if style in LAYOUT_TEMPLATES else "Modern"

        color_theme = COLOR_THEMES.get(style_key, COLOR_THEMES["Modern"])
        layout_suggestions = LAYOUT_TEMPLATES.get(style_key, LAYOUT_TEMPLATES["Modern"])

        furniture_placements = []
        for i, item in enumerate(furniture[:6]):
            furniture_placements.append({
                "product": item.get("product_name", "Unknown"),
                "position_hint": layout_suggestions[i] if i < len(layout_suggestions) else "Place as accent piece",
                "price": item.get("price"),
            })

        design_plan = {
            "style": style_key,
            "color_theme": color_theme,
            "layout_suggestions": layout_suggestions,
            "furniture_placements": furniture_placements,
            "room_analysis_summary": {
                "area_m2": analysis.get("room_area_estimate_m2"),
                "brightness": analysis.get("brightness"),
                "floor_space_pct": analysis.get("floor_space_pct"),
            },
            "design_score": self._compute_design_score(analysis),
        }

        # Save to file
        design_filename = f"design_{uuid.uuid4().hex[:8]}.json"
        design_path = os.path.join(self.output_dir, design_filename)
        with open(design_path, "w") as f:
            json.dump(design_plan, f, indent=2)

        # Persist to database
        design_record = Design(
            user_id=user_id,
            room_image_path=room_image_path,
            detected_style=style_key,
            generated_design=json.dumps(design_plan),
        )
        db.session.add(design_record)
        db.session.commit()

        design_plan["design_id"] = design_record.id
        design_plan["design_file"] = design_filename
        return design_plan

    @staticmethod
    def _compute_design_score(analysis: dict) -> int:
        """Heuristic design score (0-100)."""
        score = 60
        brightness = analysis.get("brightness", "Moderate")
        if brightness in ("Bright", "Well-Lit"):
            score += 15
        floor = analysis.get("floor_space_pct", 50)
        if floor > 60:
            score += 12
        elif floor > 40:
            score += 6
        edge = analysis.get("edge_density", 5)
        if edge < 10:
            score += 8
        return min(score, 98)
