from flask import Blueprint, jsonify
from models.product_model import ProductModel

products_bp = Blueprint("products", __name__, url_prefix="/products")

@products_bp.route("/", methods=["GET"])
def list_products():
    rows = ProductModel.list_all()
    # Já são dicts (cursor DictCursor)
    data = [{"id": r["id"], "name": r["name"], "stock": r["stock"]} for r in rows]
    return jsonify(data), 200

@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    prod = ProductModel.get(product_id)
    if not prod:
        return jsonify({"error": "Produto não encontrado"}), 404
    data = {"id": prod["id"], "name": prod["name"], "stock": prod["stock"]}
    return jsonify(data), 200
