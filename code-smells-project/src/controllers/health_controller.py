from database import get_db


def status():
    db = get_db()

    def contar(tabela):
        return db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]

    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": contar("produtos"),
            "usuarios": contar("usuarios"),
            "pedidos": contar("pedidos"),
        },
        "versao": "1.0.0",
    }, 200
