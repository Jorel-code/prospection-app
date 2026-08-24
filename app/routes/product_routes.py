# NOTE PEDAGOGIQUE : module correspondant au Guide 2 (catalogue produit),
# pas encore couvert dans votre programme. Ce blueprint n'est PAS enregistré
# dans app/__init__.py (volontairement), donc il n'interfère pas avec le
# module prospects qui fonctionne. Complétez-le quand vous arriverez au
# Guide 2 : implémentez SQLAlchemyProductRepository, puis AjouterProduct /
# AfficherProduct dans product_service.py, avant de le réactiver ici.

from flask import Blueprint, request, jsonify

product_bp = Blueprint("products", __name__)

@product_bp.route("/products", methods=["POST"])
def create_product():
    return jsonify({"error": "Module produit pas encore implémenté (voir Guide 2)."}), 501

@product_bp.route("/products/<string:product_nom>", methods=["GET"])
def get_product(product_nom):
    return jsonify({"error": "Module produit pas encore implémenté (voir Guide 2)."}), 501
