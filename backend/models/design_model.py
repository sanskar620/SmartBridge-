"""
Gruha Alankara — Design Model
"""

from datetime import datetime, timezone
from database.db import db


class Design(db.Model):
    __tablename__ = "designs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    room_image_path = db.Column(db.String(500), nullable=False)
    detected_style = db.Column(db.String(100), nullable=True)
    generated_design = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "room_image_path": self.room_image_path,
            "detected_style": self.detected_style,
            "generated_design": self.generated_design,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
