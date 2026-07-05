import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http(e):
        return jsonify({"erro": e.description, "sucesso": False}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        # Loga o detalhe internamente, mas não vaza str(e) para o cliente.
        logger.exception("erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
