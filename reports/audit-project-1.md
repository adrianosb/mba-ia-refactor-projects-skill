```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection por concatenação (AP-01)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 127-129, 140, 148-160, 174, 188, 192, 220, 224, 280, 289-297
Description: Todas as queries montam a string SQL concatenando valores vindos do request (`"... WHERE id = " + str(id)`, `"... email = '" + email + "'"`). O login em models.py:109-111 concatena email e senha direto na cláusula WHERE.
Impact: Bypass de autenticação e exfiltração/destruição do banco com um payload simples (`' OR '1'='1`).
Recommendation: Playbook §1 — trocar concatenação por queries parametrizadas com `?`.

### [CRITICAL] Credenciais hardcoded (AP-02)
File: app.py:7, app.py:8, controllers.py:289
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` e `DEBUG = True` fixos no código; o mesmo secret é devolvido no corpo de `/health`.
Impact: Qualquer commit vaza o segredo da aplicação; debug ligado expõe stack traces em produção.
Recommendation: Playbook §2 — mover para `config/settings.py` lendo variáveis de ambiente + `.env.example`.

### [CRITICAL] Senha em texto claro (AP-03)
File: models.py:110-111, models.py:127-129, database.py:76-78
Description: Senhas são gravadas e comparadas em texto puro. O seed insere `admin123`/`123456` sem hash e o login compara `senha = '<input>'` diretamente.
Impact: Vazamento do banco entrega todas as credenciais reutilizáveis.
Recommendation: Playbook §3 — `generate_password_hash` / `check_password_hash` (werkzeug) com salt.

### [CRITICAL] God File (AP-04)
File: models.py:1-314
Description: Um único arquivo concentra acesso a dados, regra de negócio (cálculo de desconto, agregação de pedido) e formatação de resposta para 4 domínios (produtos, usuários, pedidos, relatórios).
Impact: Impossível testar em isolamento; qualquer mudança em um domínio arrisca os outros.
Recommendation: Playbook §4 — separar em `models/` e `controllers/` por domínio.

### [CRITICAL] Endpoint destrutivo sem autenticação (AP-05)
File: app.py:47-57, app.py:59-78
Description: `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário vindo do body — ambos sem qualquer autenticação.
Impact: Um anônimo destrói o banco ou executa qualquer comando SQL (RCE via SQL).
Recommendation: Playbook §7 — remover a execução arbitrária e proteger rotas admin com middleware de auth.

### [HIGH] Regra de negócio na camada de dados (AP-06)
File: models.py:235-273, models.py:133-169
Description: `relatorio_vendas` calcula faixas de desconto e ticket médio dentro do model; `criar_pedido` faz toda a agregação de total e baixa de estoque no mesmo lugar do acesso a dados.
Impact: Regra não reutilizável nem testável sem banco; mistura de responsabilidades.
Recommendation: Playbook §5 — mover a regra para service/controller; model só faz acesso a dados.

### [HIGH] Estado global mutável (AP-07)
File: database.py:4, database.py:10
Description: Conexão única global (`db_connection = None`) compartilhada entre requests com `check_same_thread=False`.
Impact: Race conditions e vazamento de estado entre requisições concorrentes.
Recommendation: Playbook §8 — conexão por request via `flask.g` + teardown.

### [HIGH] Dado sensível na resposta (AP-08)
File: models.py:83, models.py:99, controllers.py:289
Description: `get_todos_usuarios` e `get_usuario_por_id` incluem o campo `senha` no dicionário retornado; `/health` devolve `secret_key`, `db_path` e `debug`.
Impact: Exfiltração passiva de senhas e configuração sensível por qualquer chamador.
Recommendation: Playbook §6 — DTO com whitelist de campos públicos.

### [HIGH] Falta de transação em fluxo multi-step (AP-09)
File: models.py:148-168
Description: `criar_pedido` insere o pedido, insere os itens e baixa o estoque em commits soltos, sem transação atômica.
Impact: Falha no meio deixa estoque baixado sem pedido, ou pedido sem itens.
Recommendation: Playbook §9 — envolver a sequência em `BEGIN/COMMIT/ROLLBACK`.

### [MEDIUM] N+1 queries (AP-10)
File: models.py:187-199, models.py:219-231
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem uma query de itens e outra de nome do produto para cada pedido, dentro do loop.
Impact: Número de queries cresce linearmente com o volume de pedidos.
Recommendation: Playbook §10 — `JOIN` ou `WHERE pedido_id IN (...)` e agrupar em memória.

### [MEDIUM] Validação ausente ou duplicada (AP-11)
File: controllers.py:28-54, controllers.py:72-90
Description: O mesmo bloco de validação de produto (nome, preço, estoque, categoria) está copiado em `criar_produto` e `atualizar_produto`, com a lista `categorias_validas` inline.
Impact: Alterar uma regra exige editar vários pontos; risco de divergência.
Recommendation: Playbook §11 — função de validação única reaproveitada pelas rotas.

### [MEDIUM] Captura genérica de exceção (AP-13)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 291-292
Description: Todo handler usa `except Exception as e: return jsonify({"erro": str(e)})`, devolvendo a mensagem interna crua ao cliente.
Impact: Mascara bugs reais e vaza detalhes de implementação.
Recommendation: Playbook §12 — handler de erro central + logging, sem expor `str(e)`.

### [LOW] print como logger (AP-14)
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: `print(...)` espalhado em controllers e no entry point para log e para simular envio de e-mail/SMS/push.
Impact: Sem controle de nível/rotação; risco de logar dado sensível.
Recommendation: Playbook §12 — `logging` estruturado.

### [LOW] Magic numbers (AP-15)
File: models.py:257-262
Description: Limites e taxas de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) soltos no cálculo do relatório.
Impact: Regra difícil de ajustar e de entender.
Recommendation: Playbook §12 — constantes nomeadas em config.

================================
Total: 14 findings
================================
```
