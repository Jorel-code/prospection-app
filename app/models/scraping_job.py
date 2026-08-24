from app.extensions import db

class ScrapingJob(db.Model):
    __tablename__ = "scraping_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    sector = db.Column(db.String(255))
    location = db.Column(db.String(255))
    keywords = db.Column(db.String(255), nullable=True)
    engine_used = db.Column(db.String(50))
    status = db.Column(db.String(20), default="pending")  # pending|running|done|failed
    results_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    finished_at = db.Column(db.DateTime, nullable=True)