# Análise de projeto (Fase 1)

Heurísticas para detectar a stack e mapear a arquitetura. São sinais, não regras rígidas — cruze mais de um antes de concluir.

## Linguagem e framework

Comece pelo manifesto de dependências:

| Arquivo | Linguagem | Onde achar o framework |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | `flask`, `django`, `fastapi` na lista |
| `package.json` | Node.js | `dependencies`: `express`, `fastify`, `koa`, `@nestjs/core` |
| `go.mod` | Go | `gin`, `echo`, `fiber` |
| `pom.xml`, `build.gradle` | Java | `spring-boot`, `spring-web` |
| `Gemfile` | Ruby | `rails`, `sinatra` |
| `composer.json` | PHP | `laravel`, `symfony` |

Confirme pelos imports no entry point. A versão sai do próprio manifesto (`flask==3.1.1`, `"express": "^4.18.0"`).

Se não houver manifesto, use a extensão dominante dos arquivos (`.py`, `.js`, `.go`) e os imports.

## Banco de dados e acesso

- **Driver/ORM** nas dependências: `sqlite3`, `psycopg2`, `mysql-connector`, `sqlalchemy`, `sequelize`, `prisma`, `mongoose`.
- **Connection string** no código ou config: `sqlite:///app.db`, `postgres://...`, `mongodb://...`. Repare em `:memory:` (banco que some no restart).
- **SQL cru vs ORM**: procure `cursor.execute(...)`, `db.query(...)` (cru) ou `Model.query`, `db.session` (ORM).

Liste as tabelas/entidades a partir de `CREATE TABLE`, definições de modelo ou queries.

## Arquitetura atual

Classifique em uma destas:

- **Monolítico** — tudo em 1 a 4 arquivos; rotas, queries e regra de negócio no mesmo lugar.
- **Camadas parciais** — existem pastas como `models/`, `routes/`, `services/`, mas a responsabilidade vaza entre elas (query dentro do route, regra dentro do model).
- **Em camadas** — separação clara de models, controllers/services e rotas.

Sinais de mistura de responsabilidade: query SQL dentro de um route handler, cálculo de negócio dentro de um model, um único arquivo com 200+ linhas fazendo de tudo.

## Domínio

Infira em uma frase a partir de nomes de tabelas, rotas e modelos. Ex.: tabelas `produtos, pedidos, usuarios` → "API de e-commerce"; `courses, enrollments` → "LMS"; `tasks, categories` → "task manager".

## Saída

Alimente o bloco `PHASE 1: PROJECT ANALYSIS` do SKILL.md com o que foi detectado aqui.
