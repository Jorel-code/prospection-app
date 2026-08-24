from flask import Blueprint, request, jsonify
from app.forms.container import get_prospect_service

prospect_bp = Blueprint("prospect_bp", __name__)

@prospect_bp.route("/prospects", methods=["POST"])
def create_prospect():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_prospect_service()
    try:
        prospect = service.create(
            user_id=1,  # à remplacer par l'utilisateur authentifié
            company_name=data.get("company_name"),
            email=data.get("email"),
            whatsapp_number=data.get("whatsapp_number"),
            notes=data.get("notes"),
            source="manual"
        )
        return jsonify({"message": "Prospect créé", "id": prospect.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
