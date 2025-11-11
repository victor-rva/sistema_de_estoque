from db import get_conn

class ProductModel:
    @staticmethod
    def list_all():
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, stock FROM products ORDER BY id;")
            rows = cur.fetchall()  # será lista de dicts
            return rows
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get(product_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, stock FROM products WHERE id=%s;", (product_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
