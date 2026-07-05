import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from database import init_db, close_db
from middlewares.error_handler import register_error_handlers
from routes.produto_routes import bp as produtos_bp
from routes.usuario_routes import bp as usuarios_bp
from routes.pedido_routes import bp as pedidos_bp
from routes.relatorio_routes import bp as relatorios_bp
from routes.health_routes import bp as health_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.config["DB_PATH"] = settings.DB_PATH

    CORS(app)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    for bp in (produtos_bp, usuarios_bp, pedidos_bp, relatorios_bp, health_bp):
        app.register_blueprint(bp)

    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    init_db(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
