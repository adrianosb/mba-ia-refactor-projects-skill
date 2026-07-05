```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (SQLAlchemy)
Files:   11 analyzed | ~1150 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Credenciais hardcoded (AP-02)
File: app.py:13, app.py:11, app.py:34, services/notification_service.py:9-10
Description: SECRET_KEY = 'super-secret-key-123' e a URI do banco fixos no código; debug=True no app.run; o NotificationService traz email_user e email_password ('senha123') hardcoded.
Impact: Qualquer commit vaza o segredo da app e a senha de e-mail; debug ligado expõe stack trace em produção.
Recommendation: Playbook §2 — mover para config/settings.py lendo variáveis de ambiente + .env.example.

### [CRITICAL] Hash de senha fraco (AP-03)
File: models/user.py:29, models/user.py:32
Description: set_password/check_password usam hashlib.md5(pwd) sem salt.
Impact: MD5 é quebrável; vazamento do banco entrega as senhas por rainbow table.
Recommendation: Playbook §3 — werkzeug generate_password_hash/check_password_hash (salt embutido).

### [HIGH] Senha exposta na resposta (AP-08)
File: models/user.py:16-25 (usado em routes/user_routes.py:33, 85, 209)
Description: User.to_dict() inclui o campo password (hash) no dicionário; ele sai em GET /users/<id>, no POST /users e no /login.
Impact: Exfiltração passiva do hash de senha por qualquer chamador.
Recommendation: Playbook §6 — to_dict() com whitelist de campos públicos, sem password.

### [HIGH] Regra de negócio nas rotas (AP-06)
File: routes/task_routes.py:30-57, 282-287; routes/user_routes.py:171-180; routes/report_routes.py:33-43, 55-68, 119-135
Description: Cálculo de "overdue" duplicado inline em 4 handlers; agregação de estatísticas e produtividade por usuário feita a mão dentro das rotas de relatório. A pasta services/ existe mas quase não é usada.
Impact: Regra não reutilizável nem testável sem subir o Flask; qualquer ajuste precisa ser replicado em vários pontos.
Recommendation: Playbook §5 — mover para controllers/services; rota só faz parse/chamar/responder. is_overdue() já existe no model e deve ser reaproveitado.

### [MEDIUM] N+1 queries (AP-10)
File: routes/task_routes.py:41-57; routes/report_routes.py:53-68
Description: get_tasks faz User.query.get e Category.query.get para cada task dentro do loop; o summary_report roda uma query de tasks por usuário no loop.
Impact: Número de queries cresce linearmente com o volume de tasks/usuários.
Recommendation: Playbook §10 — eager load (joinedload) ou agrupar em memória.

### [MEDIUM] APIs deprecated (AP-12)
File: datetime.utcnow() em models/*.py e routes/*.py (ex. task.py:15-16, task_routes.py:31); Model.query.get() em task_routes.py:67, user_routes.py:29 etc.; type(tags) == list em task_routes.py:141, 210 e utils/helpers.py:103
Description: datetime.utcnow() está deprecado (usar datetime.now(timezone.utc)); Query.get() está legado no SQLAlchemy 2.0 (usar db.session.get); type(x)==list em vez de isinstance.
Impact: Quebra/aviso em versões futuras da stack.
Recommendation: Playbook §12 — trocar pelas APIs modernas.

### [MEDIUM] Captura genérica de exceção (AP-13)
File: routes/task_routes.py:62, 236; routes/report_routes.py:186-188, 206-208, 221-223 (e demais handlers)
Description: except: nu e except Exception genérico devolvendo {'error': 'Erro interno'}, engolindo a causa real.
Impact: Mascara bugs e dificulta diagnóstico; sem tratamento central.
Recommendation: Playbook §12 — errorhandler central do Flask + logging.

### [LOW] print como logger (AP-14)
File: routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147; services/notification_service.py:21, 24; utils/helpers.py:39
Description: print(...) espalhado como log de criação/atualização/erro.
Impact: Sem controle de nível/rotação; risco de logar dado sensível.
Recommendation: Playbook §12 — módulo logging.

### [LOW] Magic numbers / constantes ignoradas (AP-15)
File: routes/user_routes.py:64, 116; routes/task_routes.py:96, 99, 113
Description: Limites de senha (<4), título (3/200) e prioridade (1-5) soltos inline nas rotas — embora utils/helpers.py:110-116 já defina MIN_TITLE_LENGTH, MIN_PASSWORD_LENGTH etc. sem serem usados.
Impact: Regra difícil de ajustar; duplicação entre helpers e rotas.
Recommendation: Playbook §12 — usar as constantes nomeadas já existentes.

================================
Total: 9 findings
================================
```
