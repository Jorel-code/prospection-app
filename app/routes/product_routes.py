from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.container import get_product_service

product_bp = Blueprint("product_bp", __name__)

@product_bp.route("/products", methods=["GET"])
@jwt_required()
def list_products():
    user_id = int(get_jwt_identity())
    service = get_product_service()
    products = service.list_all(user_id=user_id)
    return jsonify([{
        "id": p.id, "name": p.name, "description": p.description,
        "image_url": p.image_url, "demo_link": p.demo_link
    } for p in products]), 200

@product_bp.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corps de requête JSON invalide ou manquant"}), 400

    service = get_product_service()
    try:
        product = service.create(
            user_id=user_id, name=data.get("name"), description=data.get("description"),
            image_url=data.get("image_url"), demo_link=data.get("demo_link")
        )
        return jsonify({"message": "Produit créé", "id": product.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400