from app.extensions import db

class Prospect(db.Model):
    __tablename__ = "prospects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    scraping_job_id = db.Column(db.Integer, db.ForeignKey("scraping_jobs.id"), nullable=True)

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

    def has_valid_contact(self):
        return bool(self.email or self.whatsapp_number)