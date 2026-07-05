# Catálogo de anti-patterns (Fase 2)

Cada item tem severidade, sinais de detecção agnósticos de stack e a seção do playbook que resolve. Se um sinal aparece no código, registre um finding com arquivo e linha.

Escala de severidade:

- **CRITICAL** — falha de segurança ou de arquitetura que impede o funcionamento correto ou expõe dados (credencial hardcoded, SQL injection, God Class).
- **HIGH** — violação forte de MVC/SOLID que trava manutenção e testes (regra de negócio no controller, estado global mutável, acoplamento sem injeção).
- **MEDIUM** — padronização, duplicação ou performance moderada (N+1, validação ausente, API deprecated).
- **LOW** — legibilidade, nomes ruins, magic numbers.

---

## CRITICAL

### AP-01 — SQL Injection por concatenação
Sinais: `cursor.execute("... " + var)`, f-string ou template literal com valor de `request`/`req.body`/`req.params` dentro da query (`f"WHERE id = {id}"`, `` `SELECT ... ${x}` ``).
Impacto: bypass de auth, exfiltração ou destruição do banco.
Transformação: Playbook §1 (queries parametrizadas).

### AP-02 — Credenciais hardcoded
Sinais: `SECRET_KEY = "..."`, `password = "..."`, `API_KEY = "..."` com literal; connection string com senha embutida; prefixos como `sk_live_`, `AKIA`, `ghp_`.
Impacto: qualquer commit vaza o segredo.
Transformação: Playbook §2 (env vars + módulo de config).

### AP-03 — Senha em texto claro ou hash fraco
Sinais: senha salva/comparada em texto claro (`WHERE senha = '<input>'`), uso de `md5`/`sha1`/`base64` para senha, ausência de salt.
Impacto: vazamento do banco = credenciais reutilizáveis.
Transformação: Playbook §3 (bcrypt/argon2 com salt).

### AP-04 — God Class / God File
Sinais: um arquivo/classe com 200+ linhas misturando acesso a dados, regra de negócio, roteamento e validação; nome genérico (`AppManager`, `Main`, `Handler`) que inicializa o banco e registra rotas.
Impacto: impossível testar em isolamento; qualquer mudança cascateia.
Transformação: Playbook §4 (separar em Models/Controllers/Routes).

### AP-05 — Endpoint destrutivo sem autenticação
Sinais: rotas `/admin/*`, `DELETE /*`, `/reset`, `/purge` sem middleware/decorator de auth; endpoint que executa SQL vindo do body.
Impacto: destruição de dados disparável por anônimo.
Transformação: Playbook §7 (middleware de auth) + remoção de execução arbitrária.

---

## HIGH

### AP-06 — Regra de negócio no controller/route
Sinais: handler HTTP com loop de agregação, cálculo de desconto/status/total, ou cascade delete manual dentro da própria rota.
Impacto: regra não reutilizável e não testável sem subir o framework web.
Transformação: Playbook §5 (mover para service/controller; rota só faz parse/chamar/responder).

### AP-07 — Estado global mutável
Sinais: variável de módulo mutável (`cache = {}`, `total_revenue = 0`) alterada por handlers; conexão de banco única compartilhada (`check_same_thread=False`).
Impacto: race conditions, testes poluídos, vazamento de memória.
Transformação: Playbook §8 (injeção de dependência; conexão por request).

### AP-08 — Dado sensível na resposta
Sinais: `to_dict()`/`toJSON()`/serializer incluindo `password`, `token`, `secret`; `SELECT *` de usuários devolvido cru.
Impacto: exfiltração passiva de credenciais.
Transformação: Playbook §6 (DTO com whitelist de campos).

### AP-09 — Falta de transação em fluxo multi-step
Sinais: sequência de INSERT/UPDATE em tabelas relacionadas (pedido + itens + estoque) sem `BEGIN/COMMIT/ROLLBACK`.
Impacto: estado inconsistente em falha parcial (estoque baixado sem pedido criado).
Transformação: Playbook §9 (transação explícita).

---

## MEDIUM

### AP-10 — N+1 queries
Sinais: query dentro de loop sobre resultado de outra query (`for pedido in pedidos: execute("... WHERE pedido_id = ...")`).
Impacto: degradação linear conforme o volume cresce.
Transformação: Playbook §10 (`JOIN` / `WHERE id IN (...)` / eager load).

### AP-11 — Validação ausente ou duplicada
Sinais: rota que grava sem validar o body; o mesmo bloco `if not x: return 400` repetido em vários handlers; lista de valores válidos inline em vários lugares.
Impacto: dados inválidos no banco; ajuste de regra exige editar N pontos.
Transformação: Playbook §11 (função/esquema de validação único).

### AP-12 — APIs deprecated
Sinais: ver seção "APIs deprecated" abaixo, conforme a stack da Fase 1.
Impacto: quebra em versões futuras; comportamento indefinido.
Transformação: Playbook §12 (trocar pela API moderna).

### AP-13 — Captura genérica de exceção
Sinais: `except:` sem tipo; `except Exception: return str(e)`; `catch (e) { res.status(500).send(e.message) }` devolvendo o erro cru.
Impacto: mascara bugs reais e vaza detalhes internos.
Transformação: Playbook §12 e handler central (§5).

---

## LOW

### AP-14 — `print`/`console.log` como logger
Sinais: `print(...)`/`console.log(...)` espalhados em controllers e services, sem logger estruturado.
Impacto: sem controle de nível/rotação; risco de logar dado sensível.
Transformação: Playbook §12 (logger estruturado).

### AP-15 — Magic numbers e valores soltos
Sinais: números soltos em cálculos (`if total > 10000: desconto = total * 0.1`), limites inline (`if len(pwd) < 4`).
Impacto: difícil ajustar regra; legibilidade ruim.
Transformação: Playbook §12 (constantes nomeadas em config).

---

## APIs deprecated por stack

Aplique a sub-seção da linguagem detectada na Fase 1. Registre como AP-12 (MEDIUM).

### Python / Flask
- `@app.before_first_request` — removido no Flask 2.3. Usar `app.app_context()` + init explícito.
- `werkzeug.security.safe_str_cmp` — removido. Usar `hmac.compare_digest`.
- `hashlib.md5`/`sha1` para senha — quebrado (ver AP-03).
- `datetime.utcnow()` — deprecado; usar `datetime.now(timezone.utc)`.
- `collections.Mapping`/`Iterable` — movidos para `collections.abc`.
- `type(x) == list` — usar `isinstance(x, list)`.

### SQLAlchemy
- `Query.get(pk)` — usar `session.get(Model, pk)`.
- `db.engine.execute(...)` — removido no 2.0; usar `session.execute(text(...))`.

### Node.js / Express
- `body-parser` separado — usar `express.json()` / `express.urlencoded()` (Express 4.16+).
- `new Buffer(...)` — usar `Buffer.from(...)` / `Buffer.alloc(...)`.
- `crypto.createCipher(...)` — usar `createCipheriv`.
- `url.parse(...)` — usar `new URL(...)`.
- `var` em código moderno — usar `const`/`let`.
- Callbacks aninhados onde `async/await` seria natural.
