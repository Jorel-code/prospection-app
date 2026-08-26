from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.container import get_auth_service

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_auth_service()
    try:
        user = service.register(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password")
        )
        return jsonify({"message": "Compte créé", "id": user.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_auth_service()
    try:
        user = service.authenticate(email=data.get("email"), password=data.get("password"))
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token, "user_id": user.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401