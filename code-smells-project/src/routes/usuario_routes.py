from flask import Blueprint, jsonify, request

from controllers import usuario_controller

bp = Blueprint("usuarios", __name__)


@bp.get("/usuarios")
def listar():
    body, status = usuario_controller.listar()
    return jsonify(body), status


@bp.get("/usuarios/<int:id>")
def buscar(id):
    body, status = usuario_controller.buscar(id)
    return jsonify(body), status


@bp.post("/usuarios")
def criar():
    body, status = usuario_controller.criar(request.get_json(silent=True))
    return jsonify(body), status


@bp.post("/login")
def login():
    body, status = usuario_controller.login(request.get_json(silent=True) or {})
    return jsonify(body), status
