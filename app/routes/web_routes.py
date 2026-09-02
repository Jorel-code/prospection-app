"""
Routes du frontend web (pages HTML rendues côté serveur, via Jinja2).

Distinctes des routes API JSON existantes (app/routes/*_routes.py, protégées
par JWT). Ici on utilise une authentification par SESSION Flask classique,
adaptée à la navigation multi-pages d'un navigateur (impossible d'attacher
un header "Authorization: Bearer ..." à un simple lien <a href="...">).

Les deux mécanismes d'authentification (JWT pour l'API, session pour le
web) s'appuient sur le même AuthService/Argon2 en dessous — aucune
duplication de la logique de sécurité.
"""
from functools import wraps
from datetime import datetime
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

from app.container import (
    get_prospect_service,
    get_product_service,
    get_scraping_service,
    get_ai_generation_service,
    get_campaign_service,
    get_auth_service,
)

from app.extensions import db
from app.models.user import User
from app.models.prospect import Prospect
from app.models.product import Product
from app.models.scraping_job import ScrapingJob
from app.models.campaign import Campaign
from app.models.campaign_message import CampaignMessage
from app.models.idempotency_key import IdempotencyKey

web_bp = Blueprint("web", __name__)


# ---------------------------------------------------------------------------
# Authentification par session (spécifique au frontend web)
# ---------------------------------------------------------------------------

def login_required_web(fonction):
    @wraps(fonction)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("web.login"))
        return fonction(*args, **kwargs)
    return wrapper


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        service = get_auth_service()
        try:
            user = service.authenticate(
                email=request.form.get("email"),
                password=request.form.get("password"),
            )
            session["user_id"] = user.id
            return redirect(url_for("web.dashboard_page"))
        except ValueError as e:
            return render_template("login.html", error=str(e))
    return render_template("login.html")

@web_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        service = get_auth_service()
        try:
            user = service.register(
                username=request.form.get("username"),
                email=request.form.get("email"),
                password=request.form.get("password"),
            )
            session["user_id"] = user.id
            return redirect(url_for("web.dashboard_page"))
        except ValueError as e:
            return render_template("register.html", error=str(e))
    return render_template("register.html")

@web_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.login"))


@web_bp.route("/")
def index():
    return redirect(url_for("web.dashboard_page") if "user_id" in session else url_for("web.login"))


def _temps_ecoule(moment):
    """Formate une date en 'il y a X min/h/j', pour les activités récentes."""
    if not moment:
        return ""
    delta = datetime.utcnow() - moment
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "à l'instant"
    if minutes < 60:
        return f"il y a {minutes} min"
    heures = minutes // 60
    if heures < 24:
        return f"il y a {heures} h"
    return f"il y a {heures // 24} j"

def _idempotent(key, user_id, endpoint):
    """True si c'est la première fois qu'on voit cette clé (on doit exécuter),
    False si déjà traitée (double soumission à ignorer)."""
    if not key:
        return True
    if IdempotencyKey.query.filter_by(key=key).first():
        return False
    db.session.add(IdempotencyKey(key=key, user_id=user_id, endpoint=endpoint))
    db.session.commit()
    return True


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@web_bp.route("/dashboard")
@login_required_web
def dashboard_page():
    user_id = session["user_id"]

    total_prospects = Prospect.query.filter_by(user_id=user_id).count()
    nb_campagnes = Campaign.query.filter_by(user_id=user_id).count()

    total_envois = db.session.query(CampaignMessage).join(Campaign).filter(Campaign.user_id == user_id).count()
    total_reussis = db.session.query(CampaignMessage).join(Campaign).filter(
        Campaign.user_id == user_id, CampaignMessage.status == "sent"
    ).count()
    taux_reussite = round(total_reussis / total_envois * 100, 1) if total_envois else 0

    bots_actifs = ScrapingJob.query.filter_by(user_id=user_id, status="running").count()
    bots_total = ScrapingJob.query.filter_by(user_id=user_id).count()

    par_source_rows = db.session.query(
        Prospect.source, db.func.count(Prospect.id)
    ).filter(Prospect.user_id == user_id).group_by(Prospect.source).all()
    repartition_par_source = dict(par_source_rows)
    max_source_count = max(repartition_par_source.values()) if repartition_par_source else 0

    par_statut_rows = db.session.query(
        Prospect.status, db.func.count(Prospect.id)
    ).filter(Prospect.user_id == user_id).group_by(Prospect.status).all()
    repartition_par_statut = dict(par_statut_rows)

    stats = {
        "total_prospects": total_prospects,
        "nb_campagnes": nb_campagnes,
        "total_envois": total_envois,
        "taux_reussite": taux_reussite,
        "bots_actifs": bots_actifs,
        "bots_total": bots_total,
        "repartition_par_source": repartition_par_source,
        "repartition_par_statut": repartition_par_statut,
        "max_source_count": max_source_count,
    }

    # Activités récentes : derniers jobs de scraping + derniers messages envoyés
    activites = []
    for job in ScrapingJob.query.filter_by(user_id=user_id).order_by(ScrapingJob.finished_at.desc()).limit(3):
        if job.finished_at:
            activites.append({
                "titre": "Scraping terminé" if job.status == "done" else "Scraping échoué",
                "description": f"{job.results_count} prospect(s) extraits pour '{job.sector or 'tous secteurs'}'.",
                "temps": _temps_ecoule(job.finished_at),
                "couleur": "tertiary-container" if job.status == "done" else "error",
                "_dt": job.finished_at,
            })
    for msg in db.session.query(CampaignMessage).join(Campaign).filter(
        Campaign.user_id == user_id, CampaignMessage.sent_at.isnot(None)
    ).order_by(CampaignMessage.sent_at.desc()).limit(3):
        activites.append({
            "titre": "Message envoyé" if msg.status == "sent" else "Échec d'envoi",
            "description": f"Canal {msg.channel} — statut: {msg.status}.",
            "temps": _temps_ecoule(msg.sent_at),
            "couleur": "primary" if msg.status == "sent" else "error",
            "_dt": msg.sent_at,
        })
    activites.sort(key=lambda a: a["_dt"], reverse=True)

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        blob_theme="blue",
        stats=stats,
        activites_recentes=activites[:5],
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )


def _username(user_id):
    user = User.query.get(user_id)
    return user.username if user else None


def _email(user_id):
    user = User.query.get(user_id)
    return user.email if user else None


# ---------------------------------------------------------------------------
# Prospects
# ---------------------------------------------------------------------------

@web_bp.route("/app/prospects")
@login_required_web
def prospects_page():
    user_id = session["user_id"]
    prospects = Prospect.query.filter_by(user_id=user_id).order_by(Prospect.created_at.desc()).all()
    return render_template(
        "prospects.html",
        active_page="prospects",
        blob_theme="blue",
        prospects=prospects,
        idempotency_key_prospect=str(uuid.uuid4()),
        idempotency_key_csv=str(uuid.uuid4()),
        message=request.args.get("message"),
        error=request.args.get("error"),
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )


@web_bp.route("/app/prospects/create", methods=["POST"])
@login_required_web
def create_prospect():
    user_id = session["user_id"]
    idempotency_key = request.form.get("idempotency_key")
    if not _idempotent(idempotency_key, user_id, "create_prospect"):
        return redirect(url_for("web.prospects_page", message="Ce prospect a déjà été créé (double soumission ignorée)."))
    service = get_prospect_service()
    try:
        service.create(
            user_id=session["user_id"],
            company_name=request.form.get("company_name"),
            email=request.form.get("email") or None,
            whatsapp_number=request.form.get("whatsapp_number") or None,
            notes=request.form.get("notes") or None,
            source="manual",
        )
        return redirect(url_for("web.prospects_page", message="Prospect créé avec succès."))
    except ValueError as e:
        return redirect(url_for("web.prospects_page", error=str(e)))


@web_bp.route("/app/prospects/import-csv", methods=["POST"])
@login_required_web
def import_csv():
    user_id = session["user_id"]
    idempotency_key = request.form.get("idempotency_key")
    if not _idempotent(idempotency_key, user_id, "import_csv"):
        return redirect(url_for("web.prospects_page", message="Cet import a déjà été traité (double soumission ignorée)."))
    fichier = request.files.get("fichier")
    if not fichier or not fichier.filename.endswith(".csv"):
        return redirect(url_for("web.prospects_page", error="Merci de fournir un fichier .csv valide."))

    service = get_prospect_service()
    resultats = service.import_csv(user_id=session["user_id"], fichier_csv=fichier)
    message = f"{resultats['importes']} importés, {resultats['rejetes']} rejetés, {resultats['doublons']} doublons."
    return redirect(url_for("web.prospects_page", message=message))


# ---------------------------------------------------------------------------
# Produits
# ---------------------------------------------------------------------------

@web_bp.route("/app/products")
@login_required_web
def products_page():
    user_id = session["user_id"]
    produits = Product.query.filter_by(user_id=user_id).order_by(Product.created_at.desc()).all()
    return render_template(
        "products.html",
        active_page="products",
        blob_theme="neutral",
        produits=produits,
        idempotency_key_product=str(uuid.uuid4()),
        message=request.args.get("message"),
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )


@web_bp.route("/app/products/create", methods=["POST"])
@login_required_web
def create_product():
    user_id = session["user_id"]
    idempotency_key = request.form.get("idempotency_key")
    if not _idempotent(idempotency_key, user_id, "create_product"):
        return redirect(url_for("web.products_page", message="Ce produit a déjà été créé (double soumission ignorée)."))
    service = get_product_service()
    try:
        service.create(
            user_id=session["user_id"],
            name=request.form.get("name"),
            description=request.form.get("description") or None,
            image_url=request.form.get("image_url") or None,
            demo_link=request.form.get("demo_link") or None,
        )
        return redirect(url_for("web.products_page", message="Produit créé avec succès."))
    except ValueError as e:
        return redirect(url_for("web.products_page", message=str(e)))


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

@web_bp.route("/app/scraping")
@login_required_web
def scraping_page():
    user_id = session["user_id"]
    scraping_jobs = ScrapingJob.query.filter_by(user_id=user_id).order_by(ScrapingJob.created_at.desc()).all()

    prospects_scrapes = Prospect.query.filter_by(user_id=user_id, source="scraping").all()
    total_extraits = len(prospects_scrapes)
    total_valides = sum(1 for p in prospects_scrapes if p.status == "verified")
    taux_validite = round(total_valides / total_extraits * 100, 1) if total_extraits else 0

    repartition = {}
    for p in prospects_scrapes:
        repartition[p.status] = repartition.get(p.status, 0) + 1

    scraping_stats = {
        "total_extraits": total_extraits,
        "total_valides": total_valides,
        "taux_validite": taux_validite,
        "repartition": repartition,
        "pct_verified": round(repartition.get("verified", 0) / total_extraits * 100, 1) if total_extraits else 0,
        "pct_invalid": round(repartition.get("invalid", 0) / total_extraits * 100, 1) if total_extraits else 0,
        "pct_raw": round(repartition.get("raw", 0) / total_extraits * 100, 1) if total_extraits else 0,
    }

    return render_template(
        "scraping.html",
        active_page="scraping",
        blob_theme="green",
        scraping_jobs=scraping_jobs,
        scraping_stats=scraping_stats,
        message=request.args.get("message"),
        idempotency_key=str(uuid.uuid4()),
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )

@web_bp.route("/app/scraping/launch", methods=["POST"])
@login_required_web
def launch_scraping():
    import threading

    user_id = session["user_id"]
    idempotency_key = request.form.get("idempotency_key")
    if not _idempotent(idempotency_key, user_id, "launch_scraping"):
        return redirect(url_for("web.scraping_page", message="Ce scraping a déjà été lancé (double soumission ignorée)."))

    sector = request.form.get("sector")
    location = request.form.get("location")
    keywords = request.form.get("keywords")
    app_ctx = current_app._get_current_object()

    def tache_fond():
        with app_ctx.app_context():
            service = get_scraping_service()
            service.launch(user_id=user_id, sector=sector, location=location, keywords=keywords)

    threading.Thread(target=tache_fond).start()
    return redirect(url_for("web.scraping_page", message="Scraping lancé en arrière-plan. Rafraîchissez dans quelques secondes."))

# ---------------------------------------------------------------------------
# Campagnes IA
# ---------------------------------------------------------------------------

@web_bp.route("/app/campaigns")
@login_required_web
def campaigns_page():
    user_id = session["user_id"]
    prospects_verifies = Prospect.query.filter_by(user_id=user_id, status="verified").all()
    produits = Product.query.filter_by(user_id=user_id).all()

    return render_template(
        "campaigns.html",
        active_page="campaigns",
        blob_theme="violet",
        prospects_verifies=prospects_verifies,
        produits=produits,
        message=request.args.get("message"),
        error=request.args.get("error"),
        preview_message=None,
        preview_provider=None,
        idempotency_key=str(uuid.uuid4()),
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )


@web_bp.route("/app/campaigns/preview", methods=["POST"])
@login_required_web
def preview_message():
    user_id = session["user_id"]
    prospects_verifies = Prospect.query.filter_by(user_id=user_id, status="verified").all()
    produits = Product.query.filter_by(user_id=user_id).all()

    service = get_ai_generation_service()
    preview_message, preview_provider, error = None, None, None
    try:
        generated = service.generate_message(
            prospect_id=int(request.form.get("prospect_id")),
            product_id=int(request.form.get("product_id")),
            channel="email",
        )
        preview_message = generated.content
        preview_provider = generated.provider_used
    except Exception as e:
        error = f"Erreur du moteur IA : {e}"

    return render_template(
        "campaigns.html",
        active_page="campaigns",
        blob_theme="violet",
        prospects_verifies=prospects_verifies,
        produits=produits,
        message=None,
        error=error,
        preview_message=preview_message,
        preview_provider=preview_provider,
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )


@web_bp.route("/app/campaigns/launch", methods=["POST"])
@login_required_web
def launch_campaign():
    user_id = session["user_id"]
    idempotency_key = request.form.get("idempotency_key")
    if not _idempotent(idempotency_key, user_id, "launch_campaign"):
        return redirect(url_for("web.campaigns_page", message="Cette campagne a déjà été lancée (double soumission ignorée)."))
    channel = request.form.get("channel")
    prospect_ids = [int(pid) for pid in request.form.getlist("prospect_ids")]
    product_id = request.form.get("product_id")

    if not prospect_ids or not product_id:
        return redirect(url_for("web.campaigns_page", error="Sélectionnez au moins un prospect et un produit."))

    service = get_campaign_service(channel=channel)
    try:
        resultat = service.launch(
            user_id=user_id, product_id=int(product_id),
            prospect_ids=prospect_ids, channel=channel,
            name=f"Campagne du {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}",
        )
        message = f"Campagne lancée : {resultat['envoyes']} envoyé(s), {resultat['echecs']} échec(s)."
        return redirect(url_for("web.campaigns_page", message=message))
    except Exception as e:
        return redirect(url_for("web.campaigns_page", error=f"Erreur lors du lancement : {e}"))


# ---------------------------------------------------------------------------
# Intégrations (lecture seule : montre ce qui est configuré via .env)
# ---------------------------------------------------------------------------

@web_bp.route("/app/integrations")
@login_required_web
def integrations_page():
    import os
    user_id = session["user_id"]

    integrations = {
        "ia": {
            "Groq": bool(os.environ.get("GROQ_API_KEY")),
            "Google Gemini": bool(os.environ.get("GEMINI_API_KEY")),
            "Mistral AI": bool(os.environ.get("MISTRAL_API_KEY")),
            "Hugging Face": bool(os.environ.get("HF_TOKEN")),
        },
        "email": bool(os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASSWORD")),
        "whatsapp": bool(os.environ.get("WHATSAPP_ACCESS_TOKEN") and os.environ.get("WHATSAPP_PHONE_NUMBER_ID")),
    }

    return render_template(
        "integrations.html",
        active_page="integrations",
        blob_theme="blue",
        integrations=integrations,
        current_user_username=_username(user_id),
        current_user_email=_email(user_id),
    )
