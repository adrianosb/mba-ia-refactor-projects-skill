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
