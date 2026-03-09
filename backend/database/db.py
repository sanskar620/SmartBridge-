"""
Gruha Alankara — Database Initialization
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize database with the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        from models.user_model import User
        from models.design_model import Design
        from models.booking_model import Booking
        from models.product_model import Product
        db.create_all()
        _seed_products(db)


def _seed_products(db):
    """Seed the product catalog if it is empty."""
    from models.product_model import Product

    if Product.query.first() is not None:
        return

    products = [
        Product(product_name="Oslo Sofa", style="Scandinavian", price=85000, image_path="oslo_sofa.png", category="seating"),
        Product(product_name="Drift Armchair", style="Contemporary", price=32000, image_path="drift_armchair.png", category="seating"),
        Product(product_name="Nord Coffee Table", style="Minimalist", price=18500, image_path="nord_coffee_table.png", category="tables"),
        Product(product_name="Arc Floor Lamp", style="Industrial", price=12000, image_path="arc_floor_lamp.png", category="lighting"),
        Product(product_name="Tokyo Bookshelf", style="Japanese", price=45000, image_path="tokyo_bookshelf.png", category="storage"),
        Product(product_name="Mist Side Table", style="Wabi-Sabi", price=9500, image_path="mist_side_table.png", category="tables"),
        Product(product_name="Silk Pendant Light", style="Luxe Minimal", price=28000, image_path="silk_pendant_light.png", category="lighting"),
        Product(product_name="Stone Credenza", style="Modern", price=72000, image_path="stone_credenza.png", category="storage"),
        Product(product_name="Lotus Dining Table", style="Traditional", price=55000, image_path="lotus_dining_table.png", category="tables"),
        Product(product_name="Zen Floor Cushion", style="Japanese", price=4500, image_path="zen_floor_cushion.png", category="seating"),
        Product(product_name="Minimal Wall Shelf", style="Minimalist", price=8500, image_path="minimal_wall_shelf.png", category="storage"),
        Product(product_name="Warm Desk Lamp", style="Modern", price=6200, image_path="warm_desk_lamp.png", category="lighting"),
    ]
    db.session.add_all(products)
    db.session.commit()
