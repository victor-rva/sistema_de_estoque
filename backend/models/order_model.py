from db import get_conn

class OrderModel:
    @staticmethod
    def insert_with_cursor(product_id, quantity, cursor):
        cursor.execute(
            "INSERT INTO orders (product_id, quantity) VALUES (%s, %s);",
            (product_id, quantity)
        )
        return cursor.lastrowid

    @staticmethod
    def list_recent(limit=50):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT o.id, o.product_id, p.name AS product_name, o.quantity, o.created_at
                FROM orders o
                JOIN products p ON p.id = o.product_id
                ORDER BY o.created_at DESC
                LIMIT %s;
            """, (limit,))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
