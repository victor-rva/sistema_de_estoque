from db import get_conn
from models.product_model import ProductModel
from models.order_model import OrderModel

class InsufficientStock(Exception):
    """Lançada quando não há estoque suficiente. .args[0] -> quantidade disponível."""
    pass

class NotFound(Exception):
    pass

class OrderService:
    @staticmethod
    def create_order(product_id: int, quantity: int):
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        conn = get_conn()
        cur = conn.cursor()
        try:
            # inicio da transação
            conn.begin()

            # lock pessimista: bloqueia a linha do produto
            cur.execute("SELECT id, name, stock FROM products WHERE id=%s FOR UPDATE;", (product_id,))
            prod = cur.fetchone()
            if not prod:
                conn.rollback()
                raise NotFound("Product not found")

            if prod["stock"] < quantity:
                conn.rollback()
                raise InsufficientStock(prod["stock"])

            new_stock = prod["stock"] - quantity

            # atualiza estoque
            cur.execute("UPDATE products SET stock=%s WHERE id=%s;", (new_stock, product_id))

            # insere pedido
            cur.execute("INSERT INTO orders (product_id, quantity) VALUES (%s, %s);", (product_id, quantity))
            order_id = cur.lastrowid

            conn.commit()

            return {
                "orderId": order_id,
                "product": {"id": prod["id"], "name": prod["name"]},
                "quantity": quantity,
                "stockRemaining": new_stock
            }
        except:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
