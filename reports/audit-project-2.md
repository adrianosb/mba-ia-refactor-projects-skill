```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~181 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Credenciais hardcoded (AP-02)
File: src/utils.js:2-6
Description: `dbPass = "senha_super_secreta_prod_123"`, `paymentGatewayKey = "pk_live_1234567890abcdef"` (prefixo pk_live_ = chave de produção), `dbUser` e `smtpUser` fixos no objeto `config`.
Impact: Qualquer clone do repositório vaza a chave do gateway de pagamento e as credenciais do banco.
Recommendation: Playbook §2 — mover para `config/index.js` lendo `process.env` + `.env.example`.

### [CRITICAL] Hash fraco e senha nunca verificada (AP-03)
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:40-75
Description: `badCrypto()` gera um "hash" concatenando base64 num loop, sem salt e truncado a 10 chars. O seed grava a senha `'123'` em texto claro. No checkout o usuário é buscado só por email (linha 40) e a senha nunca é comparada — não há autenticação real.
Impact: Vazamento do banco entrega senhas triviais de reverter; qualquer um se autentica sabendo só o email.
Recommendation: Playbook §3 — `bcrypt.hashSync(pwd, 10)` / `compareSync`; verificar senha no login.

### [CRITICAL] God Class (AP-04)
File: src/AppManager.js:4-141
Description: A classe `AppManager` cria a conexão, monta o schema, faz o seed, registra todas as rotas e ainda contém a regra de checkout, relatório e delete — tudo num arquivo só.
Impact: Impossível testar em isolamento; qualquer alteração numa rota arrisca as outras.
Recommendation: Playbook §4 — separar em models/, controllers/, routes/ por domínio.

### [CRITICAL] Dado sensível em log (AP-08)
File: src/AppManager.js:45
Description: `console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)` grava o número completo do cartão e a chave do gateway no stdout.
Impact: Exposição de dado de cartão (PCI) e do segredo do gateway em qualquer coletor de logs.
Recommendation: Playbook §6/§12 — nunca logar cartão/segredo; logger estruturado sem dado sensível.

### [HIGH] Endpoints admin/destrutivos sem autenticação (AP-05)
File: src/AppManager.js:80-129, src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` devolve receita e alunos de todos os cursos sem auth; `DELETE /api/users/:id` apaga o usuário sem auth e deixa enrollments/payments órfãos (a própria resposta admite: "ficaram sujos no banco").
Impact: Anônimo lê o financeiro completo e corrompe a integridade referencial do banco.
Recommendation: Playbook §7 — middleware de auth nas rotas admin/delete; `ON DELETE CASCADE` ou limpeza transacional.

### [HIGH] Regra de negócio dentro da rota (AP-06)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de checkout decide status do pagamento, cria usuário, matrícula, pagamento e audit log; o de relatório agrega receita e monta o payload — toda a regra vive dentro do handler HTTP.
Impact: Regra não reutilizável nem testável sem subir o Express.
Recommendation: Playbook §5 — mover para services/controllers; rota só faz parse → chamar → responder.

### [HIGH] Estado global mutável (AP-07)
File: src/utils.js:9-10, src/AppManager.js:7
Description: `globalCache = {}` e `totalRevenue = 0` são variáveis de módulo mutadas por handlers; a conexão sqlite é única (`:memory:`) compartilhada entre todos os requests.
Impact: Race conditions e vazamento de estado entre requisições; banco some a cada restart.
Recommendation: Playbook §8 — injetar dependências; conexão gerenciada, sem cache global.

### [HIGH] Checkout sem transação (AP-09)
File: src/AppManager.js:50-63
Description: O checkout insere enrollment, depois payment, depois audit_log em callbacks encadeados soltos, sem transação atômica.
Impact: Falha no meio deixa matrícula sem pagamento (ou vice-versa) — estado inconsistente.
Recommendation: Playbook §9 — envolver a sequência numa transação com rollback.

### [MEDIUM] N+1 queries no relatório (AP-10)
File: src/AppManager.js:83-127
Description: Para cada curso busca enrollments; para cada enrollment busca user e payment em queries separadas dentro de loops aninhados.
Impact: Número de queries cresce com cursos × matrículas; degrada conforme o volume.
Recommendation: Playbook §10 — um JOIN entre courses/enrollments/users/payments.

### [MEDIUM] Validação fraca/ausente (AP-11)
File: src/AppManager.js:35, src/AppManager.js:46
Description: O checkout só checa presença dos campos; a aprovação do pagamento é decidida por `cc.startsWith("4")` (nenhuma validação de cartão/email real); `pwd` não é validado.
Impact: Dados inválidos entram no banco; lógica de pagamento é um placeholder frágil.
Recommendation: Playbook §11 — validação única (schema) na entrada da rota.

### [MEDIUM] Erros engolidos e respostas cruas (AP-13)
File: src/AppManager.js:41, src/AppManager.js:84, src/AppManager.js:133
Description: Handlers retornam strings soltas (`"Erro DB"`) e o `DELETE` ignora `err` por completo; não há tratamento de erro centralizado.
Impact: Falhas passam silenciosas; respostas inconsistentes e sem status semântico.
Recommendation: Playbook §12 + middleware de erro central.

### [MEDIUM] Callback hell / API deprecated para a stack (AP-12)
File: src/AppManager.js:37-77, src/AppManager.js:83-127
Description: Todo o acesso a dados usa a API baseada em callbacks aninhados do `sqlite3` onde `async/await` seria o padrão moderno no ecossistema Node. Não há APIs hard-deprecated (`new Buffer`, `body-parser`, `var`) — o código já usa `express.json()`.
Impact: Legibilidade ruim e propensão a erro (pyramid of doom); manutenção difícil.
Recommendation: Playbook §12 — repositórios com Promises + `async/await` nos controllers.

### [LOW] console.log como logger (AP-14)
File: src/app.js:13, src/utils.js:13, src/AppManager.js:45, src/AppManager.js:59
Description: `console.log` espalhado para boot, cache e "processamento" de pagamento, sem logger estruturado nem níveis.
Impact: Sem controle de nível/rotação; já é o vetor do vazamento de cartão (AP-08).
Recommendation: Playbook §12 — logger estruturado.

### [LOW] Magic numbers (AP-15)
File: src/AppManager.js:46, src/utils.js:19-22
Description: `startsWith("4")` como regra de aprovação, `10000` iterações e os `substring(0,2)`/`substring(0,10)` do badCrypto soltos no código.
Impact: Regras difíceis de entender e ajustar.
Recommendation: Playbook §12 — constantes nomeadas / remover badCrypto.

================================
Total: 14 findings
================================
```
