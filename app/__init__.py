from flask import Flask
from app.forms.config import Config
from app.forms.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.prospect_routes import prospect_bp
    
    app.register_blueprint(prospect_bp)
    
    with app.app_context():
        db.create_all()

    return app
