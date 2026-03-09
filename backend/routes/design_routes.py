"""
Gruha Alankara — Design Routes
Handles design generation and history.
"""

import json
import logging

from flask import Blueprint, request, jsonify, current_app

from services.style_recommendation import StyleRecommendationService
from services.furniture_search import FurnitureSearchService
from services.design_generation import DesignGenerationService
from services.image_analysis import ImageAnalysisService
from models.design_model import Design

logger = logging.getLogger(__name__)

design_bp = Blueprint("design", __name__)


@design_bp.route("/recommend-furniture", methods=["GET"])
def recommend_furniture():
    """Return AI furniture recommendations based on style and room area."""
    style = request.args.get("style", "Modern")
    room_area = request.args.get("room_area", 15.0, type=float)

    service = FurnitureSearchService()
    products = service.recommend(style, room_area)

    return jsonify({
        "success": True,
        "style": style,
        "recommended_furniture": products,
    })


@design_bp.route("/generate-design", methods=["POST"])
def generate_design():
    """Generate a complete interior design plan."""
    data = request.get_json(silent=True)
    if not data or "filename" not in data:
        return jsonify({"success": False, "error": "Missing 'filename' in request body"}), 400

    filename = data["filename"]
    user_id = data.get("user_id")

    storage_dir = current_app.config["ROOM_IMAGES_DIR"]
    output_dir = current_app.config["GENERATED_DESIGNS_DIR"]

    # Step 1: Analyze image
    img_service = ImageAnalysisService(storage_dir)
    try:
        analysis = img_service.analyze(filename)
    except (FileNotFoundError, ValueError) as e:
        return jsonify({"success": False, "error": str(e)}), 400

    # Step 2: Get style recommendation
    style_service = StyleRecommendationService()
    style_result = style_service.recommend(analysis)
    primary_style = style_result["primary_style"]

    # Step 3: Get furniture recommendations
    furniture_service = FurnitureSearchService()
    furniture = furniture_service.recommend(primary_style, analysis.get("room_area_estimate_m2", 15))

    # Step 4: Generate design plan
    design_service = DesignGenerationService(output_dir)
    design_plan = design_service.generate(
        room_image_path=filename,
        style=primary_style,
        furniture=furniture,
        analysis=analysis,
        user_id=user_id,
    )

    return jsonify({
        "success": True,
        "style": primary_style,
        "style_details": style_result,
        "design": design_plan,
        "recommended_furniture": furniture,
    })


@design_bp.route("/design-history", methods=["GET"])
def design_history():
    """Return past design records."""
    user_id = request.args.get("user_id", type=int)

    if user_id:
        designs = Design.query.filter_by(user_id=user_id).order_by(Design.created_at.desc()).all()
    else:
        designs = Design.query.order_by(Design.created_at.desc()).limit(50).all()

    results = []
    for d in designs:
        entry = d.to_dict()
        if d.generated_design:
            try:
                entry["generated_design"] = json.loads(d.generated_design)
            except (json.JSONDecodeError, TypeError):
                pass
        results.append(entry)

    return jsonify({
        "success": True,
        "designs": results,
    })


@design_bp.route("/furniture-assets", methods=["GET"])
def furniture_assets():
    """Return available furniture assets for AR visualization."""
    service = FurnitureSearchService()
    products = service.get_all_products()

    assets = []
    for p in products:
        assets.append({
            "id": p["id"],
            "name": p["product_name"],
            "style": p["style"],
            "category": p["category"],
            "price": p["price"],
            "image_path": p.get("image_path"),
            "ar_supported": True,
        })

    return jsonify({
        "success": True,
        "furniture_assets": assets,
    })
