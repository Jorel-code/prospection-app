from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app) 
    
    from app.routes.prospect_routes import prospect_bp
    from app.routes.product_routes import product_bp
    from app.routes.scraping_routes import scraping_bp
    from app.routes.campaign_routes import campaign_bp
    
    app.register_blueprint(prospect_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(scraping_bp)
    app.register_blueprint(campaign_bp)
   
    with app.app_context():
        
        db.create_all() return app