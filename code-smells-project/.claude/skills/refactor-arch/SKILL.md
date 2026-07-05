---
name: refactor-arch
description: Audita e refatora um projeto backend para o padrão MVC, independente da linguagem ou framework (Python/Flask, Node/Express, etc.). Use quando o usuário invocar /refactor-arch ou pedir para auditar arquitetura, achar code smells, organizar código legado ou migrar um projeto para MVC.
---

# refactor-arch

Audita e refatora um projeto backend para MVC. Roda em três fases: análise, auditoria e refatoração. Só modifica arquivo depois que o usuário aprovar o relatório da Fase 2.

Funciona em qualquer stack porque detecta a tecnologia na Fase 1 e aplica os mesmos princípios de MVC/SOLID — muda a sintaxe, não a ideia.

## Regras que valem para todas as fases

- Fase 1 e Fase 2 são só leitura. Nenhum arquivo é tocado até a confirmação.
- Todo finding aponta arquivo e linha. Sem isso o usuário não consegue verificar.
- A refatoração preserva o contrato externo: mesmas rotas, mesmos métodos, mesmo shape de resposta.
- Segurança vem antes de estética. Credencial vazando é falha, não detalhe.

## Fase 1 — Análise

Objetivo: entender o projeto antes de julgar.

Leia `references/project-analysis.md` para as heurísticas de detecção.

1. Liste os arquivos-fonte, ignorando `.git`, `node_modules`, `__pycache__`, `venv`, `.venv`, `dist`, `build`.
2. Detecte linguagem e framework pelo manifesto de dependências (`requirements.txt`, `package.json`, etc.) e pelos imports.
3. Detecte o banco e a forma de acesso (driver, ORM, SQL cru).
4. Infira o domínio a partir de nomes de rotas, tabelas e modelos.
5. Classifique a arquitetura atual: tudo num arquivo, camadas parciais ou já em camadas.

Imprima o resumo neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <libs relevantes>
Domain:        <domínio em 1 linha>
Architecture:  <monolítico | camadas parciais | em camadas>
Source files:  <N> files analyzed
DB tables:     <tabelas/entidades>
================================
```

Ao terminar, siga para a Fase 2.

## Fase 2 — Auditoria

Objetivo: gerar a lista de problemas e pedir confirmação antes de mudar qualquer coisa.

Leia `references/anti-patterns.md` (catálogo) e `references/report-template.md` (formato).

1. Passe cada anti-pattern do catálogo pelos arquivos-fonte. Para cada ocorrência, registre severidade, arquivo:linha, descrição, impacto e a transformação recomendada.
2. Verifique também APIs deprecated da stack detectada (seção própria no catálogo).
3. Agrupe ocorrências repetidas do mesmo anti-pattern num finding só, listando os locais.
4. Ordene por severidade: CRITICAL → HIGH → MEDIUM → LOW.
5. Renderize o relatório seguindo o template.
6. Pare e pergunte:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não modifique nada até receber uma confirmação clara (`y`, `yes`, `sim`, `s`, `ok`). Qualquer outra resposta encerra aqui.

Mínimo de 5 findings, com pelo menos 1 CRITICAL ou HIGH. Se vier menos, releia o código com mais atenção antes de apresentar.

## Fase 3 — Refatoração

Objetivo: reorganizar para MVC, resolver os findings e validar que a aplicação continua funcionando.

Leia `references/mvc-guidelines.md` (alvo) e `references/refactor-playbook.md` (transformações antes/depois).

1. Monte a estrutura de diretórios adequada à stack (ver guideline). Num projeto que já tem camadas, complete o que falta em vez de renomear o que já funciona.
2. Aplique as transformações do playbook na ordem: primeiro os CRITICAL de segurança, depois os demais CRITICAL/HIGH, depois MEDIUM e LOW oportunisticamente.
3. Mova o código para as camadas certas preservando todas as rotas.
4. Extraia configuração e segredos para um módulo de config lendo variáveis de ambiente. Crie `.env.example`.
5. Centralize o tratamento de erro num handler/middleware.
6. Deixe o entry point como composition root: só faz o wiring, sem lógica.

### Validação (obrigatória)

Antes de reportar sucesso:

1. Suba a aplicação com o comando da stack e confirme que ela inicia sem erro.
2. Bata em cada rota que existia antes e confirme status e shape equivalentes.
3. Se houver testes, rode.

Se algum passo falhar, não reporte sucesso: mostre o erro e corrija ou reverta a mudança que quebrou.

Imprima o resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios>

## Validation
  ✓ Application boots without errors
  ✓ Endpoints respond correctly (<rotas testadas>)
  ✓ Zero CRITICAL findings remaining
================================
```

## Arquivos de referência

Leia cada um quando a fase correspondente começar, não tudo de uma vez.

- `references/project-analysis.md` — detecção de linguagem, framework, banco e arquitetura (Fase 1).
- `references/anti-patterns.md` — catálogo com sinais de detecção e severidade, incluindo APIs deprecated (Fase 2).
- `references/report-template.md` — formato do relatório de auditoria (Fase 2).
- `references/mvc-guidelines.md` — responsabilidades de cada camada e layout por stack (Fase 3).
- `references/refactor-playbook.md` — transformações concretas antes/depois (Fase 3).
