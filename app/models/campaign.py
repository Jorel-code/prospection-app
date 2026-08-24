from app.extensions import db

class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    channel = db.Column(db.String(20))       # "email" | "whatsapp" | "both"
    status = db.Column(db.String(20), default="draft")  # draft|running|completed

    created_at = db.Column(db.DateTime, server_default=db.func.now())