"""
Gruha Alankara — Product Model
"""

from database.db import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "style": self.style,
            "price": self.price,
            "image_path": self.image_path,
            "category": self.category,
        }
