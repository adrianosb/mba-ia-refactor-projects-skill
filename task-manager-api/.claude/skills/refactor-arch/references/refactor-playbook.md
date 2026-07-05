# Playbook de refatoração (Fase 3)

Transformações concretas, antes/depois, uma por anti-pattern. Os exemplos são em Python/Flask e Node/Express; adapte a sintaxe à stack detectada, mas mantenha a ideia.

---

## §1 — SQL Injection → query parametrizada

**Antes**
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```
**Depois**
```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```
Node: troque `` db.query(`... ${x}`) `` por `db.query("... WHERE id = ?", [x])`. Nunca interpole valor de request direto na string.

---

## §2 — Credenciais hardcoded → config por env var

**Antes**
```python
SECRET_KEY = "minha-chave-super-secreta-123"
```
**Depois** — `config/settings.py`
```python
import os
SECRET_KEY = os.environ["SECRET_KEY"]           # obrigatória, falha cedo
DB_URL     = os.environ.get("DB_URL", "sqlite:///app.db")
```
Crie `.env.example` listando cada variável com placeholder e garanta `.env` no `.gitignore`.

---

## §3 — Senha em texto claro / hash fraco → bcrypt

**Antes**
```python
if user["senha"] == request.json["senha"]:   # texto claro
```
**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# no cadastro
hash = generate_password_hash(senha)
# no login
if check_password_hash(user["senha_hash"], senha):
```
Node: `bcrypt.hashSync(senha, 10)` e `bcrypt.compareSync(senha, hash)`.

---

## §4 — God Class → separar em camadas

**Antes** — `models.py` com tudo: conexão, query, regra e rota.
**Depois** — divida por responsabilidade e domínio:
```
models/produto_model.py       # só acesso a dados de produto
controllers/produto_controller.py  # orquestra o fluxo
routes/produto_routes.py      # associa path -> controller
```
Mova cada trecho para a camada correspondente sem mudar o comportamento. Comece pelo domínio com mais linhas.

---

## §5 — Regra de negócio no controller → service/controller enxuto

**Antes**
```python
@app.route("/pedidos/<id>")
def get_pedido(id):
    pedido = query_pedido(id)
    total = 0
    for item in pedido["itens"]:            # regra dentro da rota
        total += item["preco"] * item["qtd"]
    if total > 1000: total *= 0.9
    return jsonify(total=total)
```
**Depois** — rota chama, service calcula:
```python
# services/pedido_service.py
def calcular_total(pedido):
    total = sum(i["preco"] * i["qtd"] for i in pedido["itens"])
    return total * DESCONTO if total > LIMITE_DESCONTO else total

# routes
@bp.route("/pedidos/<id>")
def get_pedido(id):
    pedido = pedido_model.buscar(id)
    return jsonify(total=pedido_service.calcular_total(pedido))
```

---

## §6 — Dado sensível na resposta → DTO com whitelist

**Antes**
```python
return jsonify(user)          # inclui senha_hash, token...
```
**Depois**
```python
def user_public(u):
    return {"id": u["id"], "nome": u["nome"], "email": u["email"]}

return jsonify(user_public(user))
```
Whitelist dos campos públicos, nunca blacklist.

---

## §7 — Endpoint sem auth → middleware de autenticação

**Antes**
```python
@app.route("/admin/reset", methods=["POST"])
def reset():
    db.drop_all()
```
**Depois**
```python
def require_auth(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        if not token_valido(request.headers.get("Authorization")):
            return jsonify(error="unauthorized"), 401
        return fn(*a, **k)
    return wrapper

@bp.route("/admin/reset", methods=["POST"])
@require_auth
def reset(): ...
```
Node: `router.post("/admin/reset", requireAuth, handler)`. Remova endpoints que executam SQL/comando vindo do body.

---

## §8 — Estado global mutável → injeção de dependência

**Antes**
```python
conn = sqlite3.connect("app.db", check_same_thread=False)  # global compartilhada
```
**Depois** — conexão por request/contexto:
```python
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db: db.close()
```

---

## §9 — Falta de transação → transação explícita

**Antes**
```python
insere_pedido(...)
baixa_estoque(...)     # se falhar aqui, pedido fica órfão
```
**Depois**
```python
try:
    conn.execute("BEGIN")
    insere_pedido(conn, ...)
    baixa_estoque(conn, ...)
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

---

## §10 — N+1 queries → uma query com JOIN/IN

**Antes**
```python
pedidos = query("SELECT * FROM pedidos")
for p in pedidos:
    p["itens"] = query("SELECT * FROM itens WHERE pedido_id = ?", (p["id"],))
```
**Depois**
```python
ids = [p["id"] for p in pedidos]
itens = query(f"SELECT * FROM itens WHERE pedido_id IN ({placeholders(ids)})", ids)
# agrupa itens por pedido_id em memória
```
Com ORM, use eager loading (`joinedload` / `include` / `.populate()`).

---

## §11 — Validação ausente/duplicada → validação única

**Antes** — o mesmo bloco `if not nome: return 400` copiado em create e update.
**Depois**
```python
def validar_produto(data):
    erros = []
    if not data.get("nome"): erros.append("nome obrigatório")
    if data.get("preco", 0) <= 0: erros.append("preco deve ser positivo")
    return erros

# na rota
erros = validar_produto(request.json)
if erros: return jsonify(errors=erros), 400
```
Onde houver biblioteca de schema (Pydantic, Marshmallow, Zod, Joi), prefira ela.

---

## §12 — Qualidade: deprecated, exceção, logging, magic numbers

**API deprecated** — troque pela equivalente moderna:
```python
datetime.utcnow()            # antes
datetime.now(timezone.utc)   # depois
```
```js
new Buffer(x)                // antes
Buffer.from(x)               // depois
```

**Exceção genérica → específica + handler central**
```python
# antes
try: ...
except: pass
# depois
@app.errorhandler(Exception)
def handle(e):
    app.logger.exception(e)
    return jsonify(error="internal error"), 500
```

**print → logger**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("pedido criado id=%s", pedido_id)
```

**Magic number → constante nomeada**
```python
# antes: if total > 10000: desconto = total * 0.1
LIMITE_DESCONTO = 10000
TAXA_DESCONTO   = 0.1
if total > LIMITE_DESCONTO: desconto = total * TAXA_DESCONTO
```
