from flask import Blueprint, request, jsonify
from app.container import get_ai_generation_service
from app.container import get_campaign_service

campaign_bp = Blueprint("campaign_bp", __name__)

@campaign_bp.route("/messages/generate", methods=["POST"])
def generate_message():
    data = request.get_json(silent=True) or {}
    service = get_ai_generation_service()
    try:
        generated = service.generate_message(
            prospect_id=data.get("prospect_id"),
            product_id=data.get("product_id"),
            channel=data.get("channel")
        )
        return jsonify({
            "message": generated.content,
            "provider_used": generated.provider_used
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erreur du moteur IA", "detail": str(e)}), 502

@campaign_bp.route("/campaigns/launch", methods=["POST"])
def launch_campaign():
    data = request.get_json(silent=True) or {}
    service = get_campaign_service()
    resultat = service.launch(
        user_id=1, product_id=data.get("product_id"),
        prospect_ids=data.get("prospect_ids", []),
        channel=data.get("channel"), name=data.get("name", "Campagne sans nom")
    )
    return jsonify(resultat), 200