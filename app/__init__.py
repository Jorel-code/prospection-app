from flask import Flask, render_template
from flask_talisman import Talisman
from flask_cors import CORS
from app.config import Config
from app.extensions import db, jwt, limiter
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.configurer_logs()

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # En-têtes de sécurité automatiques (CSP, HSTS, X-Frame-Options...)
    # force_https=False pour le développement local ; passe à True en production
    csp = {
        "default-src": "'self'",
        "script-src": ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "img-src": ["'self'", "data:", "https:"],
    }
    Talisman(app, force_https=False, content_security_policy=csp)

    # CORS restreint : remplace par l'URL réelle de ton frontend le moment venu
    CORS(app, origins=["http://localhost:3000"])

    from app.models.user import User
    from app.models.prospect import Prospect
    from app.models.product import Product
    from app.models.scraping_job import ScrapingJob
    from app.models.campaign import Campaign
    from app.models.campaign_message import CampaignMessage

    from app.routes.auth_routes import auth_bp
    from app.routes.prospect_routes import prospect_bp
    from app.routes.product_routes import product_bp
    from app.routes.scraping_routes import scraping_bp
    from app.routes.campaign_routes import campaign_bp
    from app.routes.web_routes import web_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(prospect_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(scraping_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(web_bp)

    @app.errorhandler(404)
    def page_non_trouvee(e):
        return render_template("erreur.html", code=404, message="Page introuvable."), 404

    @app.errorhandler(500)
    def erreur_serveur(e):
        return render_template("erreur.html", code=500, message="Une erreur interne est survenue."), 500

    with app.app_context():
        jobs_orphelins = ScrapingJob.query.filter(ScrapingJob.status.in_(["pending", "running"])).all()
        for job in jobs_orphelins:
            job.status = "failed"
            job.finished_at = datetime.utcnow()
        if jobs_orphelins:
            db.session.commit()
            print(f"[Startup] {len(jobs_orphelins)} job(s) orphelin(s) marqué(s) comme échoués.")
    return app