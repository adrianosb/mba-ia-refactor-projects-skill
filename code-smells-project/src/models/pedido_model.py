from database import get_db


def _itens_por_pedido(db, pedido_ids):
    """Busca os itens de todos os pedidos em uma query só (evita N+1)."""
    if not pedido_ids:
        return {}
    placeholders = ",".join("?" * len(pedido_ids))
    rows = db.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
        "p.nome AS produto_nome "
        "FROM itens_pedido ip "
        "LEFT JOIN produtos p ON p.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders})",
        pedido_ids,
    ).fetchall()
    agrupado = {}
    for r in rows:
        agrupado.setdefault(r["pedido_id"], []).append({
            "produto_id": r["produto_id"],
            "produto_nome": r["produto_nome"] or "Desconhecido",
            "quantidade": r["quantidade"],
            "preco_unitario": r["preco_unitario"],
        })
    return agrupado


def _montar(db, rows):
    itens = _itens_por_pedido(db, [r["id"] for r in rows])
    return [{
        "id": r["id"],
        "usuario_id": r["usuario_id"],
        "status": r["status"],
        "total": r["total"],
        "criado_em": r["criado_em"],
        "itens": itens.get(r["id"], []),
    } for r in rows]


def listar_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM pedidos").fetchall()
    return _montar(db, rows)


def listar_por_usuario(usuario_id):
    db = get_db()
    rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    return _montar(db, rows)


def atualizar_status(pedido_id, status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
    db.commit()


def criar(usuario_id, itens):
    db = get_db()

    total = 0
    linhas = []
    for item in itens:
        produto = db.execute(
            "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
        ).fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total += produto["preco"] * item["quantidade"]
        linhas.append((produto, item["quantidade"]))

    # Pedido + itens + baixa de estoque em uma transação atômica.
    try:
        cur = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cur.lastrowid
        for produto, quantidade in linhas:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, produto["id"], quantidade, produto["preco"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (quantidade, produto["id"]),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"pedido_id": pedido_id, "total": total}


def estatisticas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0

    def contar(status):
        return db.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)
        ).fetchone()[0]

    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento,
        "pendentes": contar("pendente"),
        "aprovados": contar("aprovado"),
        "cancelados": contar("cancelado"),
    }
