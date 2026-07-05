import logging

from config import settings
from models import pedido_model

logger = logging.getLogger(__name__)


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return {"erro": "Usuario ID é obrigatório"}, 400
    if not itens:
        return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return {"erro": resultado["erro"], "sucesso": False}, 400

    logger.info("pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id)
    _notificar(resultado["pedido_id"])
    return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def listar_por_usuario(usuario_id):
    return {"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}, 200


def listar_todos():
    return {"dados": pedido_model.listar_todos(), "sucesso": True}, 200


def atualizar_status(pedido_id, dados):
    novo_status = dados.get("status", "")
    if novo_status not in settings.STATUS_VALIDOS:
        return {"erro": "Status inválido"}, 400
    pedido_model.atualizar_status(pedido_id, novo_status)
    logger.info("pedido %s status=%s", pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


def _notificar(pedido_id):
    # Placeholder de notificação (email/sms/push). Antes eram prints soltos.
    logger.info("notificação: pedido %s recebido", pedido_id)
