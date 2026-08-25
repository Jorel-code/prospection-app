from flask import Blueprint, request, jsonify
from app.container import get_prospect_service

prospect_bp = Blueprint("prospect_bp", __name__)

@prospect_bp.route("/prospects", methods=["GET"])
def list_prospects():
    service = get_prospect_service()
    prospects = service.prospect_repository.find_all(user_id=2)
    return jsonify([{
        "id": p.id, "company_name": p.company_name, "email": p.email,
        "whatsapp_number": p.whatsapp_number, "status": p.status, "source": p.source
    } for p in prospects]), 200

@prospect_bp.route("/prospects", methods=["POST"])
def create_prospect():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_prospect_service()
    try:
        prospect = service.create(
            user_id=2, company_name=data.get("company_name"),
            email=data.get("email"), whatsapp_number=data.get("whatsapp_number"),
            notes=data.get("notes"), source="manual"
        )
        return jsonify({"message": "Prospect créé", "id": prospect.id, "statut": prospect.status, "source": prospect.source}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@prospect_bp.route("/prospects/import-csv", methods=["POST"])
def import_csv():
    if "fichier" not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    fichier = request.files["fichier"]
    if not fichier.filename.endswith(".csv"):
        return jsonify({"error": "Le fichier doit être un .csv"}), 400

    service = get_prospect_service()
    resultats = service.import_csv(user_id=2, fichier_csv=fichier)
    return jsonify(resultats), 200