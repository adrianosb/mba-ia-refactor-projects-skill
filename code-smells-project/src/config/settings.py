import os

# Segredos e configuração lidos do ambiente. Nada hardcoded.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DB_PATH = os.environ.get("DB_PATH", "loja.db")

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

# Faixas de desconto do relatório: (faturamento mínimo, taxa).
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
