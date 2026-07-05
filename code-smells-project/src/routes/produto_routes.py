from flask import Blueprint, jsonify, request

from controllers import produto_controller

bp = Blueprint("produtos", __name__)


@bp.get("/produtos")
def listar():
    body, status = produto_controller.listar()
    return jsonify(body), status


@bp.get("/produtos/busca")
def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    body, status = produto_controller.buscar_lista(termo, categoria, preco_min, preco_max)
    return jsonify(body), status


@bp.get("/produtos/<int:id>")
def buscar_um(id):
    body, status = produto_controller.buscar(id)
    return jsonify(body), status


@bp.post("/produtos")
def criar():
    body, status = produto_controller.criar(request.get_json(silent=True))
    return jsonify(body), status


@bp.put("/produtos/<int:id>")
def atualizar(id):
    body, status = produto_controller.atualizar(id, request.get_json(silent=True))
    return jsonify(body), status


@bp.delete("/produtos/<int:id>")
def deletar(id):
    body, status = produto_controller.deletar(id)
    return jsonify(body), status
