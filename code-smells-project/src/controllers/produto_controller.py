import logging

from config import settings
from models import produto_model

logger = logging.getLogger(__name__)


def validar_produto(dados):
    if not dados:
        return ["Dados inválidos"]
    for campo, msg in (("nome", "Nome é obrigatório"),
                       ("preco", "Preço é obrigatório"),
                       ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            return [msg]
    erros = []
    if dados["preco"] < 0:
        erros.append("Preço não pode ser negativo")
    if dados["estoque"] < 0:
        erros.append("Estoque não pode ser negativo")
    if len(dados["nome"]) < 2:
        erros.append("Nome muito curto")
    if len(dados["nome"]) > 200:
        erros.append("Nome muito longo")
    if dados.get("categoria", "geral") not in settings.CATEGORIAS_VALIDAS:
        erros.append("Categoria inválida. Válidas: " + str(settings.CATEGORIAS_VALIDAS))
    return erros


def listar():
    produtos = produto_model.listar()
    logger.info("listando %d produtos", len(produtos))
    return {"dados": produtos, "sucesso": True}, 200


def buscar(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200


def buscar_lista(termo, categoria, preco_min, preco_max):
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200


def criar(dados):
    erros = validar_produto(dados)
    if erros:
        return {"erro": erros[0]}, 400
    id = produto_model.criar(
        dados["nome"], dados.get("descricao", ""), dados["preco"],
        dados["estoque"], dados.get("categoria", "geral"),
    )
    logger.info("produto criado id=%s", id)
    return {"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar(id, dados):
    if not produto_model.buscar_por_id(id):
        return {"erro": "Produto não encontrado"}, 404
    erros = validar_produto(dados)
    if erros:
        return {"erro": erros[0]}, 400
    produto_model.atualizar(
        id, dados["nome"], dados.get("descricao", ""), dados["preco"],
        dados["estoque"], dados.get("categoria", "geral"),
    )
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar(id):
    if not produto_model.buscar_por_id(id):
        return {"erro": "Produto não encontrado"}, 404
    produto_model.deletar(id)
    logger.info("produto %s deletado", id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200
