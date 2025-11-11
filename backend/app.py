from flask import Flask
from flask_cors import CORS
import os

from routes.products import products_bp
from routes.orders import orders_bp
from routes.admin_products import admin_products_bp  # novo import

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config["JSON_SORT_KEYS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Blueprints principais
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    # Rotas administrativas (CRUD de produtos)
    app.register_blueprint(admin_products_bp)

    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
