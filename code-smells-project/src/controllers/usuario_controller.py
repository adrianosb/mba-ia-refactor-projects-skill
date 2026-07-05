import logging

from werkzeug.security import generate_password_hash, check_password_hash

from models import usuario_model

logger = logging.getLogger(__name__)


def listar():
    return {"dados": usuario_model.listar(), "sucesso": True}, 200


def buscar(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {"dados": usuario, "sucesso": True}, 200


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400
    id = usuario_model.criar(nome, email, generate_password_hash(senha))
    logger.info("usuário criado email=%s", email)
    return {"dados": {"id": id}, "sucesso": True}, 201


def login(dados):
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400

    row = usuario_model.buscar_por_email(email)
    if row and check_password_hash(row["senha"], senha):
        usuario = {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
        logger.info("login ok email=%s", email)
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200

    logger.info("login falhou email=%s", email)
    return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
