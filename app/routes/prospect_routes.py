from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.container import get_prospect_service

prospect_bp = Blueprint("prospect_bp", __name__)

@prospect_bp.route("/prospects", methods=["GET"])
@jwt_required()
def list_prospects():
    user_id = int(get_jwt_identity())
    service = get_prospect_service()
    prospects = service.prospect_repository.find_all(user_id=user_id)
    return jsonify([{
        "id": p.id, "company_name": p.company_name, "email": p.email,
        "whatsapp_number": p.whatsapp_number, "status": p.status, "source": p.source
    } for p in prospects]), 200

@prospect_bp.route("/prospects", methods=["POST"])
@jwt_required()
def create_prospect():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_prospect_service()
    try:
        prospect = service.create(
            user_id=user_id, company_name=data.get("company_name"),
            email=data.get("email"), whatsapp_number=data.get("whatsapp_number"),
            notes=data.get("notes"), source="manual"
        )
        return jsonify({"message": "Prospect créé", "id": prospect.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@prospect_bp.route("/prospects/import-csv", methods=["POST"])
@jwt_required()
def import_csv():
    user_id = int(get_jwt_identity())
    if "fichier" not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    fichier = request.files["fichier"]
    if not fichier.filename.endswith(".csv"):
        return jsonify({"error": "Le fichier doit être un .csv"}), 400

    service = get_prospect_service()
    resultats = service.import_csv(user_id=user_id, fichier_csv=fichier)
    return jsonify(resultats), 200