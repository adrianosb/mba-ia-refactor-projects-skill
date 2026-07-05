# Refatoração Arquitetural com Skills

Repositório do desafio de criação de uma Skill para auditar e refatorar projetos legados para o padrão MVC.

## Análise Manual

Cada problema está classificado por severidade, e a coluna **Impacto** justifica por que ele é relevante.

### code-smells-project (Python/Flask — API de E-commerce)

API monolítica de e-commerce em 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`), sem separação real de camadas. A lista abaixo não cobre todos os problemas, apenas os de maior impacto arquitetural e de segurança.

| Severidade | Problema | Impacto | Arquivo |
|---|---|---|---|
| CRITICAL | **SQL Injection generalizado** — quase todas as queries montadas por concatenação de string com dados da requisição | Um `email` como `' OR '1'='1` em `login_usuario` (linha 110) derruba a autenticação. Qualquer endpoint com input do usuário é explorável para vazar ou destruir dados. | models.py (múltiplas linhas) |
| CRITICAL | **Endpoints administrativos sem autenticação** — `POST /admin/query` executa SQL arbitrário do corpo; `POST /admin/reset-db` apaga todas as tabelas | Acesso total ao banco para qualquer um, sem barreira. Permite ler, alterar ou zerar toda a base. | app.py (47, 59–78) |
| CRITICAL | **Senhas em texto puro e segredo exposto** — senhas sem hash e retornadas na listagem; `SECRET_KEY` hardcoded e devolvida pelo `/health` | Vazamento direto de credenciais de todos os usuários e do segredo da aplicação. | database.py, models.py, app.py, controllers.py |
| HIGH | **God module misturando dados, regra de negócio e notificações** — acesso ao banco, cálculo de total, controle de estoque e desconto no mesmo arquivo; envio de e-mail/SMS/push vazando para o controller | Sem camada de serviço, nada é testável em isolamento e qualquer mudança arrisca quebrar o resto. | models.py (arquivo inteiro), controllers.py (208–210) |
| MEDIUM | **Queries N+1 na listagem de pedidos** — uma query por pedido para buscar itens e mais uma por item para buscar o produto | N pedidos com M itens geram dezenas de idas ao banco onde um `JOIN` resolveria. Degrada conforme a base cresce. | models.py (187–199, 219–231) |
| MEDIUM | **Código duplicado** — `get_pedidos_usuario`/`get_todos_pedidos` quase idênticas; mesmo bloco de validação repetido entre criar/atualizar produto | Correções e mudanças precisam ser feitas em vários lugares, aumentando o risco de inconsistência. | models.py (171–233), controllers.py (24–96) |
| LOW | **Magic numbers nas regras de desconto** — faixas e percentuais (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) soltos no código | Regra de negócio implícita e difícil de ajustar sem ler o código linha a linha. | models.py (256–262) |
| LOW | **`print` como log** — toda a observabilidade feita com `print` | Sem níveis nem controle do que vai para a saída em produção; dificulta diagnóstico e polui os logs. | controllers.py (8, 57, 161, 179 e outros) |

### ecommerce-api-legacy (Node.js/Express — LMS API com checkout)

API de cursos em 3 arquivos (`app.js`, `AppManager.js`, `utils.js`), com um `AppManager` que centraliza banco, rotas e regra de negócio. Abaixo os problemas de maior impacto.

| Severidade | Problema | Impacto | Arquivo |
|---|---|---|---|
| CRITICAL | **Credenciais hardcoded** — senha do banco, chave do gateway de pagamento (`pk_live_...`) e usuário SMTP fixos no código | Segredos de produção versionados no repositório. Vazam para qualquer um com acesso ao código e não podem ser rotacionados sem alterar o fonte. | utils.js (2–5) |
| CRITICAL | **Dado de cartão em log e senha em texto puro** — número do cartão impresso no `console.log` junto da chave do gateway; senha `'123'` gravada sem hash no seed | Exposição de dado sensível de pagamento nos logs e credenciais em claro no banco. | AppManager.js (18, 45) |
| HIGH | **God Class** — a mesma classe cria as tabelas, define todas as rotas e executa a lógica de checkout, pagamento e relatório | Sem separação de camadas, nada é testável em isolamento e qualquer alteração numa rota arrisca quebrar o resto. | AppManager.js (arquivo inteiro) |
| HIGH | **Checkout sem atomicidade** — matrícula, pagamento e log são `INSERT`s encadeados sem transação | Se um passo falha no meio, a matrícula fica gravada sem pagamento (ou vice-versa), deixando o banco em estado inconsistente. | AppManager.js (50–63) |
| HIGH | **Hash caseiro inseguro** — `badCrypto` concatena base64 num loop e trunca em 10 caracteres | Não é criptografia real: sem salt, reversível e com colisões triviais. As senhas ficam desprotegidas mesmo "hasheadas". | utils.js (17–23) |
| MEDIUM | **Query N+1 no relatório financeiro** — uma query por curso, depois uma por matrícula e mais duas por aluno, controladas por contadores manuais | Dezenas de idas ao banco onde um `JOIN` resolveria; degrada conforme a base cresce e o encadeamento de callbacks é frágil. | AppManager.js (83–128) |
| MEDIUM | **Delete sem integridade referencial** — apaga o usuário e deixa matrículas e pagamentos órfãos (a própria resposta admite) | Registros órfãos corrompem os relatórios e não há `ON DELETE CASCADE` nem limpeza dos dados relacionados. | AppManager.js (131–137) |
| LOW | **Nomes de variáveis ruins** — `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, curso e cartão | Código ilegível; o leitor precisa rastrear o uso de cada letra para entender o fluxo do checkout. | AppManager.js (29–33) |
| LOW | **Magic string na validação do cartão** — pagamento aprovado só se `cc.startsWith("4")` | Regra implícita e sem sentido de negócio explícito; comportamento difícil de entender e de ajustar. | AppManager.js (46) |

### task-manager-api (Python/Flask — API de Task Manager)

Projeto já com alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas a organização é superficial: regra de negócio vive nas rotas e há problemas sérios de segurança. Abaixo os de maior impacto.

| Severidade | Problema | Impacto | Arquivo |
|---|---|---|---|
| CRITICAL | **Senhas hasheadas com MD5 sem salt** — `set_password`/`check_password` usam `hashlib.md5` | MD5 é quebrado e sem salt fica vulnerável a rainbow tables; as senhas ficam desprotegidas mesmo "hasheadas". | models/user.py (29, 32) |
| CRITICAL | **Segredos hardcoded** — `SECRET_KEY` fixa no código e credenciais SMTP (`email_password = 'senha123'`) versionadas | Segredos de produção expostos no repositório; vazam para qualquer um com acesso ao código e não podem ser rotacionados sem alterar o fonte. | app.py (13), services/notification_service.py (7–10) |
| HIGH | **Hash da senha vazado nas respostas** — `to_dict` do usuário inclui o campo `password`, retornado no cadastro, no login e nas listagens | Expõe o hash de todos os usuários pela API, facilitando ataques de quebra offline. | models/user.py (21) |
| HIGH | **`debug=True` e `host='0.0.0.0'`** — servidor sobe em modo debug exposto na rede | O debugger do Werkzeug permite execução de código arbitrário via navegador; não pode ir para produção. | app.py (34) |
| MEDIUM | **Query N+1** — `get_tasks` busca usuário e categoria de cada task dentro do loop; o relatório repete uma query de tasks por usuário | Dezenas de idas ao banco onde um `JOIN` resolveria; degrada conforme a base cresce. | routes/task_routes.py (41–57), routes/report_routes.py (53–68) |
| MEDIUM | **Regra de negócio duplicada nas rotas** — o cálculo de "overdue" é copiado em 4 lugares mesmo existindo `Task.is_overdue()`, e o validador `process_task_data` em `helpers.py` nunca é usado | Correções precisam ser feitas em vários pontos e o código morto engana quem lê; alto risco de inconsistência. | routes/task_routes.py, routes/user_routes.py, routes/report_routes.py, utils/helpers.py |
| LOW | **Imports não utilizados** — `os, sys, json, datetime` em `app.py`, `json, os, sys, time` nas rotas e vários módulos em `helpers.py` sem uso | Poluição visual que sugere dependências inexistentes e dificulta a leitura. | app.py (7), routes/task_routes.py (7), utils/helpers.py (1–7) |
| LOW | **`print` como log** — observabilidade feita com `print` espalhado pelas rotas | Sem níveis nem controle do que vai para a saída em produção; dificulta diagnóstico e polui os logs. | routes/task_routes.py (149, 219), routes/user_routes.py (83, 147) |


## 2. Construção da Skill

### Decisões de design

O `SKILL.md` é o prompt: descreve o fluxo das 3 fases e as regras que valem sempre (fases 1 e 2 só leem, todo finding aponta arquivo e linha, a refatoração preserva as rotas). O conhecimento de domínio fica em 5 arquivos de referência, um por área exigida no desafio:

| Arquivo | Área | Usado na |
|---|---|---|
| `references/project-analysis.md` | Detecção de linguagem, framework, banco e arquitetura | Fase 1 |
| `references/anti-patterns.md` | Catálogo com sinais de detecção e severidade + APIs deprecated | Fase 2 |
| `references/report-template.md` | Formato do relatório de auditoria | Fase 2 |
| `references/mvc-guidelines.md` | Camadas do MVC alvo e layout por stack | Fase 3 |
| `references/refactor-playbook.md` | Transformações antes/depois | Fase 3 |

Separei o conhecimento do fluxo por dois motivos: manter o `SKILL.md` curto (ele carrega sempre) e deixar cada referência ser lida só quando a fase começa, em vez de tudo de uma vez. Assim ajustar o catálogo ou o playbook não mexe no prompt principal.

O gate entre a Fase 2 e a Fase 3 é o ponto central: a skill imprime o relatório, pergunta `Proceed with refactoring (Phase 3)? [y/n]` e só continua com uma confirmação clara. Nada é escrito em disco antes disso.

### Catálogo de anti-patterns

São 15 anti-patterns (AP-01 a AP-15), com severidade distribuída e escolhidos a partir dos problemas que encontrei na análise manual dos 3 projetos:

| Severidade | Anti-patterns | Por que entraram |
|---|---|---|
| CRITICAL | SQL injection, credenciais hardcoded, senha em texto claro/hash fraco, God Class, endpoint destrutivo sem auth | São os problemas de segurança e arquitetura que aparecem nos 3 projetos e violam o MVC de forma mais grave (ex.: `AppManager` e `models.py` concentrando tudo). |
| HIGH | Regra de negócio no controller, estado global mutável, dado sensível na resposta, falta de transação | Violações de SOLID que travam teste e manutenção — como o checkout sem atomicidade e o `to_dict` vazando o hash. |
| MEDIUM | N+1, validação ausente/duplicada, APIs deprecated, captura genérica de exceção | Duplicação e performance que apareceram nos 3 (o N+1 em todos, a validação repetida entre criar/atualizar). |
| LOW | `print` como log, magic numbers | Legibilidade e observabilidade — comuns e fáceis de corrigir. |

Incluí a detecção de **APIs deprecated** como item próprio (AP-12), com uma seção por stack (Flask, SQLAlchemy, Express), já que o desafio exige recomendar o equivalente moderno — ex.: `datetime.utcnow()` → `datetime.now(timezone.utc)`, `new Buffer()` → `Buffer.from()`.

O playbook responde a cada anti-pattern com uma transformação numerada (§1 a §12), sempre com código antes/depois em Python e Node.

### Como garanti que é agnóstica de tecnologia

A skill detecta a stack na Fase 1 (pelo manifesto de dependências e imports) e só então decide o layout. As referências descrevem **padrões de detecção**, não comandos de uma linguagem: "query com valor de request interpolado" em vez de uma sintaxe fixa. Os exemplos do catálogo e do playbook vêm em Python/Flask e Node/Express lado a lado, e as guidelines trazem o layout de diretórios das duas stacks. Há ainda uma regra explícita para projetos que já têm camadas (como o `task-manager-api`): completar o que falta em vez de renomear o que já funciona, evitando churn.

### Desafios encontrados

- **Equilibrar tamanho e cobertura.** Os arquivos de referência podiam ficar enormes. Mantive o playbook enxuto (uma transformação por anti-pattern) apontando que engrossar catálogo e playbook é a iteração normal caso a skill detecte pouco.
- **Não quebrar projetos já organizados.** O 3º projeto já tem `models/`, `routes/`, `services/`. Adicionei em `mvc-guidelines.md` uma seção específica de "camadas parciais" para a skill não reestruturar do zero.
- **Preservar comportamento.** Como a refatoração move muito código, a Fase 3 tem validação obrigatória (boot da aplicação + bater em cada rota original) antes de reportar sucesso.


## 3. Resultados

> A skill foi executada nos três projetos: **code-smells-project**, **ecommerce-api-legacy** e **task-manager-api**.

### Resumo da auditoria — code-smells-project

Relatório completo em [`reports/audit-project-1.md`](reports/audit-project-1.md).

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---:|---:|---:|---:|---:|
| code-smells-project | Python/Flask 3.1.1 | 5 | 4 | 3 | 2 | 14 |

Os 5 CRITICAL são os de segurança/arquitetura: SQL injection generalizado, credenciais hardcoded, senha em texto puro, God file (`models.py` com 314 linhas) e os dois endpoints `/admin/*` sem autenticação.

### Estrutura antes/depois

```
antes                          depois
─────────────────────          ──────────────────────────────
app.py         (88 L)          src/app.py              composition root (create_app)
controllers.py (292 L)         src/config/settings.py  env vars, constantes
models.py      (314 L)  God    src/database.py         conexão por request + seed
database.py    (86 L)          src/models/             produto, usuario, pedido
                               src/controllers/        produto, usuario, pedido, relatorio, health
                               src/routes/             5 Blueprints (só roteamento)
                               src/middlewares/        error_handler central
                               .env.example

4 arquivos, ~780 linhas        ~15 módulos em 6 camadas
```

### Checklist de validação — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio descrito corretamente (API de E-commerce)
- [x] Número de arquivos analisados condiz com a realidade (4)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (14 encontrados)
- [x] Detecção de APIs deprecated incluída (nenhuma no código)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados (produto, usuario, pedido)
- [x] Views/Routes separadas para roteamento (Blueprints)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`src/app.py` só faz o wiring)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

Correções de segurança que alteram o contrato de saída (sinalizadas): `senha` removida de `/usuarios`, `secret_key`/`db_path`/`debug` removidos de `/health`, e os endpoints `/admin/query` e `/admin/reset-db` removidos (executavam SQL arbitrário sem auth). Senhas do seed passaram a ser gravadas com hash (`werkzeug.security`), então o login continua funcionando com as mesmas credenciais.

### Log da aplicação rodando após a refatoração

```
$ python src/app.py
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
INFO werkzeug 127.0.0.1 - - "GET /health HTTP/1.1" 200 -
INFO werkzeug 127.0.0.1 - - "GET /produtos HTTP/1.1" 200 -
INFO werkzeug 127.0.0.1 - - "GET /usuarios HTTP/1.1" 200 -
INFO werkzeug 127.0.0.1 - - "POST /login HTTP/1.1" 200 -
INFO werkzeug 127.0.0.1 - - "GET /relatorios/vendas HTTP/1.1" 200 -
```

Sweep completo das 17 rotas (leitura, escrita, validação e checagens de segurança) passou: `/usuarios` sem campo `senha`, `/health` sem segredos, `/admin/*` respondendo 404.

### Validação com curl

Servidor real no ar (`python src/app.py`, porta 5000), todas as rotas conferidas com `curl`:

| Método | Rota | Status | O que valida |
|---|---|---:|---|
| GET | `/` | 200 | índice |
| GET | `/health` | 200 | sem `secret_key`/`db_path`/`debug` |
| GET | `/produtos` | 200 | listagem |
| GET | `/produtos/1` | 200 | busca por id |
| GET | `/produtos/busca?q=Mouse` | 200 | busca parametrizada |
| GET | `/usuarios` | 200 | **sem o campo `senha`** |
| GET | `/usuarios/1` | 200 | busca por id |
| GET | `/pedidos` | 200 | listagem |
| POST | `/login` (senha certa) | 200 | hash funcionando |
| POST | `/login` (senha errada) | 401 | credencial inválida |
| POST | `/usuarios` | 201 | cadastro |
| POST | `/produtos` | 201 | criação |
| POST | `/produtos` (preço < 0) | 400 | validação |
| PUT | `/produtos/2` | 200 | atualização |
| POST | `/pedidos` | 201 | pedido + baixa de estoque (transação) |
| GET | `/pedidos/usuario/2` | 200 | pedidos do usuário |
| PUT | `/pedidos/1/status` | 200 | mudança de status |
| GET | `/relatorios/vendas` | 200 | cálculo de desconto |
| DELETE | `/produtos/10` | 200 | remoção |
| GET | `/produtos/9999` | 404 | not found central |
| POST | `/admin/query` | 404 | endpoint removido |
| POST | `/admin/reset-db` | 404 | endpoint removido |

### Observação sobre a stack

No monolito Flask a Fase 3 criou toda a estrutura MVC do zero — não havia camada nenhuma para aproveitar. A conexão global com `check_same_thread=False` virou conexão por request via `flask.g`, e as queries concatenadas viraram parametrizadas sem mudar as rotas. A comparação com o Node/Express está logo abaixo; falta só o Flask já parcialmente organizado (`task-manager-api`).

---

### Resumo da auditoria — ecommerce-api-legacy

Relatório completo em [`reports/audit-project-2.md`](reports/audit-project-2.md).

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---:|---:|---:|---:|---:|
| ecommerce-api-legacy | Node.js/Express 4.18.2 | 4 | 4 | 4 | 2 | 14 |

Os 4 CRITICAL: credenciais hardcoded (chave `pk_live_...` do gateway em `utils.js`), hash caseiro (`badCrypto`) com senha nunca verificada, God class (`AppManager.js`, 141 linhas com DB + rotas + regra) e o número do cartão + a chave do gateway impressos no log durante o checkout.

### Estrutura antes/depois — ecommerce-api-legacy

```
antes                          depois
─────────────────────          ──────────────────────────────
src/app.js       (14 L)        src/app.js              composition root (buildApp)
src/AppManager.js (141 L) God  src/config/index.js     env vars + loader de .env
src/utils.js     (25 L) segredo src/db/                connection (Promises) + seed
                               src/models/             user, course, enrollment, payment, audit, report
                               src/services/           checkout (transação), report (JOIN)
                               src/controllers/        checkout, report, user
                               src/routes/             3 routers (só roteamento)
                               src/middlewares/        auth (Bearer) + errorHandler
                               src/utils/              logger, password (scrypt), http
                               .env.example

3 arquivos, ~181 linhas        ~23 módulos em 7 camadas
```

### Checklist de validação — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio descrito corretamente (LMS com checkout de cursos)
- [x] Número de arquivos analisados condiz com a realidade (3)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (14 encontrados)
- [x] Detecção de APIs deprecated incluída (callback hell do `sqlite3`; sem `new Buffer`/`body-parser`)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded, segredos via `process.env`)
- [x] Models criados para abstrair dados (6 entidades, queries parametrizadas)
- [x] Views/Routes separadas para roteamento (3 routers)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/errorHandler.js`)
- [x] Entry point claro (`src/app.js` só faz o wiring)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

Correções de segurança que alteram o contrato (sinalizadas): `/api/admin/financial-report` e `DELETE /api/users/:id` passaram a exigir `Authorization: Bearer <ADMIN_TOKEN>` (401 sem token); o delete agora faz cascade cleanup e responde `{"msg":"Usuário e vínculos removidos"}` no lugar da mensagem que admitia deixar dados órfãos. O `badCrypto` foi trocado por `scrypt` com salt; os segredos saíram do código para `.env`.

### Log da aplicação rodando após a refatoração

```
$ npm start
{"ts":"2026-07-05T18:33:55.759Z","level":"info","msg":"server.started","port":3000}
{"ts":"2026-07-05T18:33:56.922Z","level":"info","msg":"checkout.payment","course_id":2,"status":"PAID"}
{"ts":"2026-07-05T18:33:56.989Z","level":"info","msg":"checkout.payment","course_id":1,"status":"DENIED"}
```

Log estruturado e sem dado sensível: o `course_id` e o `status` aparecem, mas o número do cartão e a chave do gateway (que o legado imprimia em `AppManager.js:45`) não.

### Validação com curl — ecommerce-api-legacy

Servidor real no ar (`npm start`, porta 3000), rotas conferidas com `curl`:

| Método | Rota | Status | O que valida |
|---|---|---:|---|
| POST | `/api/checkout` (cartão 4…) | 200 | sucesso, `{msg, enrollment_id}` |
| POST | `/api/checkout` (cartão 5…) | 400 | pagamento recusado |
| POST | `/api/checkout` (campos ausentes) | 400 | `Bad Request` |
| POST | `/api/checkout` (curso inexistente) | 404 | `Curso não encontrado` |
| GET | `/api/admin/financial-report` (sem token) | 401 | auth exigida |
| GET | `/api/admin/financial-report` (com token) | 200 | shape preservado, receita por curso |
| DELETE | `/api/users/1` (sem token) | 401 | auth exigida |
| DELETE | `/api/users/1` (com token) | 200 | cascade cleanup |
| GET | `/api/admin/financial-report` (após o delete) | 200 | Clean Architecture zera (`revenue:0, students:[]`) — sem matrícula/pagamento órfão |

Retornos reais da rodada limpa: checkout de sucesso devolveu `{"msg":"Sucesso","enrollment_id":2}`; o relatório com token trouxe `Clean Architecture` (997, Leonan) e `Docker` (497, Guilherme); após o `DELETE /api/users/1` o mesmo relatório mostrou o Clean Architecture zerado, confirmando o cascade.

### Observação sobre a stack (Node/Express)

Aqui o problema central era uma God class com SQL cru em callbacks aninhados, não um monolito de arquivo único como no Flask. A skill manteve a ideia das camadas e adaptou a sintaxe: a transação virou `db.transaction()` sobre a API do `sqlite3` promissificada, o relatório com 4 níveis de callback aninhado (N+1) virou um `JOIN` agregado em memória, e o hash caseiro foi para `scrypt` nativo. As rotas e os shapes de resposta continuaram os mesmos — só as duas rotas admin ganharam o gate de autenticação, sinalizado acima.

---

### Resumo da auditoria — task-manager-api

Relatório completo em [`reports/audit-project-3.md`](reports/audit-project-3.md).

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---:|---:|---:|---:|---:|
| task-manager-api | Python/Flask 3.0.0 | 2 | 2 | 3 | 2 | 9 |

Os 2 CRITICAL são de segurança: `SECRET_KEY` e a senha de SMTP hardcoded (`services/notification_service.py`), e o hash de senha em MD5 sem salt. Os 2 HIGH são o hash de senha exposto no JSON de `/users` e `/login`, e a regra de negócio (cálculo de "overdue" e agregações de relatório) espalhada dentro das rotas.

### Estrutura antes/depois — task-manager-api

Diferente dos outros dois, este projeto **já vinha com camadas parciais** (`models/`, `routes/`, `services/`, `utils/`). A Fase 3 completou o que faltava em vez de reestruturar do zero.

```
antes                                depois
───────────────────────────         ──────────────────────────────
app.py       (35 L) config fixa      config.py            NOVO — env vars, sem hardcoded
                    + rotas           .env.example         NOVO
database.py                          app.py               composition root (create_app)
seed.py                              models/              hash werkzeug, to_dict sem password
models/      to_dict com password    controllers/         NOVO — task, user, report
routes/      lógica dentro (~740 L)  routes/              3 Blueprints finos (parse→controller)
services/    creds hardcoded         services/            creds via config, logging
utils/       constantes sem uso      middlewares/         NOVO — error_handler central
                                     utils/               utcnow() + constantes usadas

camadas parciais, lógica nas rotas   MVC completo, rotas só roteiam
```

### Checklist de validação — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + SQLAlchemy)
- [x] Domínio descrito corretamente (API de Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (11)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (9 encontrados)
- [x] Detecção de APIs deprecated incluída (`datetime.utcnow()`, `Query.get()`, `type() ==`)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados (user, task, category)
- [x] Views/Routes separadas para roteamento (Blueprints finos)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`app.py` só faz o wiring)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

Correção de segurança que altera o contrato de saída (sinalizada): o campo `password` foi removido do JSON de `/users`, `/users/<id>`, `POST /users` e `/login`. As senhas do seed passaram a ser gravadas com `werkzeug.security`, então o login continua funcionando com as mesmas credenciais. Todo o resto (métodos, paths, status, demais campos) permanece idêntico.

### Log da aplicação rodando após a refatoração

```
$ python app.py
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5001
INFO werkzeug: 127.0.0.1 - - "GET /health HTTP/1.1" 200 -
INFO werkzeug: 127.0.0.1 - - "GET /tasks HTTP/1.1" 200 -
INFO werkzeug: 127.0.0.1 - - "GET /reports/summary HTTP/1.1" 200 -
INFO werkzeug: 127.0.0.1 - - "GET /users HTTP/1.1" 200 -
INFO werkzeug: 127.0.0.1 - - "POST /login HTTP/1.1" 200 -
```

(Porta 5001 porque a 5000 estava ocupada por outro processo na máquina; o `app.py` sobe na 5000 por padrão.)

### Validação com curl — task-manager-api

Servidor real no ar (porta 5001), as 22 rotas conferidas uma a uma (26 casos, incluindo validações e erros):

| Método | Rota | Status | O que valida |
|---|---|---:|---|
| GET | `/` | 200 | índice |
| GET | `/health` | 200 | boot sem expor config |
| GET | `/tasks` | 200 | listagem (JOIN, sem N+1) |
| GET | `/tasks/1` | 200 | busca por id + `overdue` |
| GET | `/tasks/search?status=pending` | 200 | busca parametrizada |
| GET | `/tasks/stats` | 200 | agregação em controller |
| GET | `/users` | 200 | **sem o campo `password`** |
| GET | `/users/1` | 200 | usuário + tasks |
| GET | `/users/1/tasks` | 200 | tasks do usuário |
| GET | `/reports/summary` | 200 | agregação em memória (sem N+1) |
| GET | `/reports/user/1` | 200 | relatório por usuário |
| GET | `/categories` | 200 | listagem |
| GET | `/tasks/9999` | 404 | not found |
| POST | `/tasks` | 201 | criação |
| POST | `/tasks` (título curto) | 400 | validação |
| PUT | `/tasks/1` | 200 | atualização |
| DELETE | `/tasks/1` | 200 | remoção |
| POST | `/users` | 201 | cadastro (sem `password` na resposta) |
| POST | `/users` (email repetido) | 409 | conflito |
| PUT | `/users/1` | 200 | atualização |
| DELETE | `/users/4` | 200 | remoção + cascade das tasks |
| POST | `/login` (senha certa) | 200 | hash werkzeug funcionando |
| POST | `/login` (senha errada) | 401 | credencial inválida |
| POST | `/categories` | 201 | criação |
| PUT | `/categories/1` | 200 | atualização |
| DELETE | `/categories/5` | 200 | remoção |

O cascade do `DELETE /users` foi confirmado: criando um usuário com uma task e apagando o usuário, a task some (`GET /tasks/<id>` → 404). Nenhuma rota devolveu 500 no log do servidor.

### Observação sobre a stack (Flask já organizado)

Este foi o caso mais próximo do dia a dia: o projeto não estava quebrado, só mal-distribuído. A skill respeitou as pastas existentes e resistiu à tentação de renomear `routes/` para `views/` só por template — o ganho foi mover a lógica que estava nas rotas para `controllers/` e completar as camadas ausentes (`config`, `middlewares`). Comparado ao monolito do projeto 1, onde criou tudo do zero, aqui a mesma skill fez o oposto: **subtraiu duplicação e realocou**, sem churn desnecessário. É a evidência de que as guidelines de "projeto com camadas parciais" funcionam — a Fase 3 se adapta ao ponto de partida em vez de aplicar um layout fixo.
