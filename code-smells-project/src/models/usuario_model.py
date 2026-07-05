from database import get_db


def _public(row):
    # Whitelist: nunca devolve o campo `senha`.
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [_public(r) for r in rows]


def buscar_por_id(id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (id,)).fetchone()
    return _public(row) if row else None


def buscar_por_email(email):
    # Retorna a linha completa (inclui o hash) só para o fluxo de login.
    return get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def criar(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cur = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cur.lastrowid
