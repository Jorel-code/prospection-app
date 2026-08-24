from app.forms.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    

class Prospect(db.Model):
    __tablename__ = "prospects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    facebook_url = db.Column(db.String(500), nullable=True)
    whatsapp_number = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    source = db.Column(db.String(20), nullable=False)     # "manual" | "csv" | "scraping"
    status = db.Column(db.String(20), default="raw")       # "raw" | "verified" | "invalid"

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("user_id", "email", name="uq_user_email"),
        db.UniqueConstraint("user_id", "whatsapp_number", name="uq_user_whatsapp"),
    )





