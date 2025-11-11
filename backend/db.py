import pymysql
import os

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "rootpwd")
DB_NAME = os.environ.get("DB_NAME", "inventory_db")

def get_conn():
    """
    Retorna uma conexão pymysql com cursor dict (facilita leitura por chave).
    autocommit=False para controlar transações manualmente.
    """
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor
    )
