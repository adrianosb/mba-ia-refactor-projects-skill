from flask import Blueprint, jsonify, request

from controllers import pedido_controller

bp = Blueprint("pedidos", __name__)


@bp.post("/pedidos")
def criar():
    body, status = pedido_controller.criar(request.get_json(silent=True))
    return jsonify(body), status


@bp.get("/pedidos")
def listar_todos():
    body, status = pedido_controller.listar_todos()
    return jsonify(body), status


@bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_por_usuario(usuario_id):
    body, status = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify(body), status


@bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status(pedido_id):
    body, status = pedido_controller.atualizar_status(pedido_id, request.get_json(silent=True) or {})
    return jsonify(body), status
