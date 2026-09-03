from flask import request, jsonify
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.container import get_ai_generation_service, get_campaign_service
from app.models.campaign_message import CampaignMessage
from app.extensions import db
from app.extensions import limiter

campaign_bp = Blueprint("campaign_bp", __name__)

@campaign_bp.route("/messages/generate", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def generate_message():
    data = request.get_json(silent=True) or {}
    service = get_ai_generation_service()
    try:
        generated = service.generate_message(
            prospect_id=data.get("prospect_id"),
            product_id=data.get("product_id"),
            channel=data.get("channel")
        )
        return jsonify({"message": generated.content, "provider_used": generated.provider_used}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erreur du moteur IA", "detail": str(e)}), 502

@campaign_bp.route("/campaigns/launch", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def launch_campaign():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    service = get_campaign_service(channel=data.get("channel"))
    resultat = service.launch(
        user_id=user_id, product_id=data.get("product_id"),
        prospect_ids=data.get("prospect_ids", []),
        channel=data.get("channel"), name=data.get("name", "Campagne sans nom")
    )
    return jsonify(resultat), 200

@campaign_bp.route("/campaigns/<int:campaign_id>/stats", methods=["GET"])
@jwt_required()
def campaign_stats(campaign_id):
    """Statistiques d'envoi d'une campagne"""
    from app.models.campaign import Campaign

    user_id = int(get_jwt_identity())
    campaign = Campaign.query.get(campaign_id)

    if not campaign or campaign.user_id != user_id:
        return jsonify({"error": "Campagne introuvable"}), 404

    messages = CampaignMessage.query.filter_by(campaign_id=campaign_id).all()
    stats = {
        "total": len(messages),
        "envoyes": sum(1 for m in messages if m.status == "sent"),
        "echecs": sum(1 for m in messages if m.status == "failed"),
        "en_attente": sum(1 for m in messages if m.status in ("pending", "queued")),
    }
    stats["taux_reussite"] = round(stats["envoyes"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
    return jsonify(stats), 200

@campaign_bp.route("/dashboard/global", methods=["GET"])
@jwt_required()
def dashboard_global():
    """Vue globale : répartition des prospects par source et statut, pour l'utilisateur connecté uniquement"""
    from app.models.prospect import Prospect
    from app.models.campaign import Campaign

    user_id = int(get_jwt_identity())

    total_prospects = Prospect.query.filter_by(user_id=user_id).count()

    total_envois = db.session.query(CampaignMessage).join(Campaign).filter(Campaign.user_id == user_id).count()
    total_reussis = db.session.query(CampaignMessage).join(Campaign).filter(
        Campaign.user_id == user_id, CampaignMessage.status == "sent"
    ).count()

    par_source = db.session.query(
        Prospect.source, db.func.count(Prospect.id)
    ).filter(Prospect.user_id == user_id).group_by(Prospect.source).all()

    par_statut_prospect = db.session.query(
        Prospect.status, db.func.count(Prospect.id)
    ).filter(Prospect.user_id == user_id).group_by(Prospect.status).all()

    return jsonify({
        "total_prospects": total_prospects,
        "total_envois": total_envois,
        "total_reussis": total_reussis,
        "repartition_par_source": dict(par_source),
        "repartition_par_statut": dict(par_statut_prospect)
    }), 200