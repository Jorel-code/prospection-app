from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models.user import User
    from app.models.prospect import Prospect
    from app.models.product import Product
    from app.models.scraping_job import ScrapingJob
    from app.models.campaign import Campaign
    from app.models.campaign_message import CampaignMessage

    from app.routes.prospect_routes import prospect_bp
    from app.routes.product_routes import product_bp
    from app.routes.scraping_routes import scraping_bp

    app.register_blueprint(prospect_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(scraping_bp)
    
    return app