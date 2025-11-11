from flask import Blueprint, request, jsonify
from services.order_service import OrderService, InsufficientStock, NotFound
from models.order_model import OrderModel

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/", methods=["GET"])
def list_orders():
    rows = OrderModel.list_recent()
    data = []
    for r in rows:
        # r é dict por conta do DictCursor
        created_at = r["created_at"]
        created_at_str = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
        data.append({
            "id": r["id"],
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "quantity": r["quantity"],
            "created_at": created_at_str
        })
    return jsonify(data), 200

@orders_bp.route("/", methods=["POST"])
def create_order():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "JSON inválido"}), 400
    product_id = payload.get("productId")
    quantity = payload.get("quantity")

    if product_id is None or quantity is None:
        return jsonify({"error": "productId e quantity são obrigatórios"}), 400

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"error": "productId e quantity devem ser inteiros"}), 400

    try:
        result = OrderService.create_order(product_id, quantity)
        return jsonify(result), 201
    except InsufficientStock as e:
        return jsonify({"error": "Estoque insuficiente", "available": int(e.args[0])}), 409
    except NotFound:
        return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro interno", "detail": str(e)}), 500
