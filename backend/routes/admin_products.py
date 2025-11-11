from flask import Blueprint, jsonify, request
from db import get_conn

admin_products_bp = Blueprint("admin_products", __name__, url_prefix="/admin/products")


@admin_products_bp.route("/", methods=["POST"])
def create_product():
    """Cria um novo produto no catálogo."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400
    name = data.get("name")
    stock = data.get("stock", 0)

    if not name:
        return jsonify({"error": "Campo 'name' é obrigatório"}), 400

    try:
        stock = int(stock)
        if stock < 0:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "Campo 'stock' deve ser um número inteiro >= 0"}), 400

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO products (name, stock) VALUES (%s, %s)", (name, stock))
        conn.commit()
        return jsonify({"id": cur.lastrowid, "name": name, "stock": stock}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Erro ao criar produto", "detail": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@admin_products_bp.route("/<int:product_id>", methods=["PATCH"])
def update_stock(product_id):
    """Atualiza o estoque de um produto existente."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    action = data.get("action")
    amount = data.get("amount")

    if action not in ("add", "remove"):
        return jsonify({"error": "Campo 'action' deve ser 'add' ou 'remove'"}), 400

    try:
        amount = int(amount)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "Campo 'amount' deve ser inteiro > 0"}), 400

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, stock FROM products WHERE id=%s FOR UPDATE", (product_id,))
        prod = cur.fetchone()
        if not prod:
            return jsonify({"error": "Produto não encontrado"}), 404

        new_stock = prod["stock"] + amount if action == "add" else prod["stock"] - amount
        if new_stock < 0:
            return jsonify({"error": "Estoque insuficiente"}), 409

        cur.execute("UPDATE products SET stock=%s WHERE id=%s", (new_stock, product_id))
        conn.commit()
        return jsonify({"id": product_id, "new_stock": new_stock}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Erro ao atualizar estoque", "detail": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@admin_products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Busca o produto
        cur.execute("SELECT id, stock FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404

        stock = product["stock"]

        # Bloqueia se ainda houver estoque
        if stock > 0:
            return jsonify({
                "error": f"Produto não pode ser removido: estoque atual é {stock}."
            }), 409

        # Exclui produto
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        return jsonify({"message": "Produto removido com sucesso"}), 200

    except Exception as e:
        conn.rollback()
        import traceback
        print(" ERRO AO EXCLUIR PRODUTO:")
        traceback.print_exc()
        return jsonify({"error": "Erro ao remover produto", "detail": str(e)}), 500
    finally:
        cur.close()
        conn.close()
