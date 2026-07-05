# Guidelines de MVC (Fase 3)

Alvo da refatoração. As camadas existem em qualquer stack; o que muda é o layout de arquivos.

## Camadas e responsabilidades

- **Config** — lê configuração e segredos de variáveis de ambiente. Sem valor hardcoded.
- **Models** — dados e acesso ao banco. Definição de entidade, queries parametrizadas, métodos de instância (`to_dict`, `check_password`). Sem regra de negócio de aplicação e sem HTTP.
- **Controllers** — orquestração do fluxo. Recebe do roteamento, chama models/services, devolve o resultado. É onde a lógica de aplicação vive.
- **Views/Routes** — roteamento: associa método+path a um controller, lê o request e serializa a resposta. Sem lógica de negócio.
- **Middlewares** — cross-cutting: tratamento de erro, autenticação, logging.
- **Services** (opcional) — regra de negócio reutilizável entre controllers. Crie só quando a mesma regra aparece em 2+ lugares.
- **Entry point** — composition root: só faz o wiring das dependências, sem lógica.

Regra geral: uma rota só faz parse → chamar → responder. Query só no model. Regra de negócio no controller ou service. Nada de segredo no código.

## Layout por stack

### Python / Flask
```
src/
├── config/settings.py
├── models/<entidade>_model.py
├── controllers/<entidade>_controller.py
├── routes/<entidade>_routes.py      # Blueprints
├── middlewares/error_handler.py
└── app.py                            # composition root
.env.example
```

### Node.js / Express
```
src/
├── config/index.js
├── models/<entidade>.model.js
├── controllers/<entidade>.controller.js
├── routes/<entidade>.routes.js       # Routers
├── middlewares/errorHandler.js
└── app.js                            # composition root
.env.example
```

## Projeto que já tem camadas parciais

Não reestruture do zero. Respeite as convenções que já existem:

- Mova a regra de negócio que vazou para dentro das rotas para o controller/service.
- Remova duplicação entre camadas.
- Adicione o que falta: config lendo env vars, middleware de erro, logger.
- Corrija os problemas de segurança e qualidade mesmo com as pastas já OK.

Não crie pasta nova para cada problema nem renomeie `routes/` para `views/` só por template — isso é churn e dificulta a revisão.

## Contrato a preservar

Depois da refatoração, toda rota que existia antes responde no mesmo método e path, com o mesmo shape de resposta. Se algum campo mudar (ex.: remover `password` do JSON), avise explicitamente no resumo final.
