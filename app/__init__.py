from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import des modèles AVANT db.create_all(), sinon SQLAlchemy
    # ne connaît pas leurs tables et ne les crée pas.
    from app.models.user import User
    from app.models.prospect import Prospect
    from app.models.product import Product
    from app.models.scraping_job import ScrapingJob
    from app.models.campaign import Campaign
    from app.models.campaign_message import CampaignMessage

    with app.app_context():
        db.create_all()

    return app