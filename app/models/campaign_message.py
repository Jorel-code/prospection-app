from app.extensions import db

class CampaignMessage(db.Model):
    __tablename__ = "campaign_messages"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospects.id"), nullable=False)

    generated_message = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")  # pending|queued|sent|failed
    error_detail = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("campaign_id", "prospect_id", name="uq_campaign_prospect"),
    )