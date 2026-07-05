from flask import Blueprint, jsonify

from controllers import health_controller

bp = Blueprint("health", __name__)


@bp.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@bp.get("/health")
def health():
    body, status = health_controller.status()
    return jsonify(body), status
