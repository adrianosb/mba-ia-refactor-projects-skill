from flask import Blueprint, jsonify

from controllers import relatorio_controller

bp = Blueprint("relatorios", __name__)


@bp.get("/relatorios/vendas")
def vendas():
    body, status = relatorio_controller.vendas()
    return jsonify(body), status
