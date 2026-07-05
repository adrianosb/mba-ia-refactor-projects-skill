from config import settings
from models import pedido_model


def _desconto(faturamento):
    for minimo, taxa in settings.FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * taxa
    return 0


def vendas():
    stats = pedido_model.estatisticas()
    faturamento = stats["faturamento"]
    total = stats["total_pedidos"]
    desconto = _desconto(faturamento)

    relatorio = {
        "total_pedidos": total,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total, 2) if total > 0 else 0,
    }
    return {"dados": relatorio, "sucesso": True}, 200
