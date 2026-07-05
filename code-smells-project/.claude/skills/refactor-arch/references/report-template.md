# Template do relatório de auditoria (Fase 2)

Renderize exatamente neste formato. Findings ordenados por severidade, CRITICAL primeiro.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<N> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [SEVERIDADE] <nome do anti-pattern> (<AP-id>)
File: <arquivo>:<linha ou intervalo>
Description: <o que foi detectado neste local, específico>
Impact: <risco concreto de segurança, correção ou manutenção>
Recommendation: <transformação do playbook a aplicar>

### [SEVERIDADE] <próximo finding>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Regras:

- Cada finding aponta arquivo e linha reais. Sem "código em geral".
- Ocorrências do mesmo anti-pattern em vários locais viram um finding só, com a lista de arquivos:linha em `File:`.
- A descrição cita o que aquele trecho faz, não a definição genérica do anti-pattern.
- Se estiver salvando o relatório em `reports/audit-<projeto>.md`, grave o mesmo conteúdo (sem a linha final de confirmação).
