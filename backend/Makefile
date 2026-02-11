.PHONY: help install setup test test-e2e lint format clean run-quick run-load run-upsert

# Variáveis
PYTHON := python
PIP := pip
VENV := .venv
JSON_PATH ?= ./tests/sample_ndjson.json
TABLE_NAME ?= teste
CHUNKSIZE ?= 5000

# Cores para output
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento (testes, lint)
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov black isort flake8

setup: ## Setup completo (venv + install + .env)
	@echo "$(BLUE)1. Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Ambiente virtual criado$(NC)"
	@echo "$(BLUE)2. Instalando dependências...$(NC)"
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Arquivo .env criado (edite com suas credenciais)$(NC)"; \
	fi
	@echo "$(GREEN)✓ Setup concluído!$(NC)"

test: ## Executa testes unitários
	pytest tests/ -v --tb=short

test-e2e: ## Executa testes de integração com MySQL
	pytest tests/ -v -m e2e --tb=short

test-cov: ## Executa testes com cobertura
	pytest tests/ -v --cov=src --cov-report=html
	@echo "$(GREEN)✓ Relatório em htmlcov/index.html$(NC)"

lint: ## Valida código com flake8
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

format: ## Formata código com black e isort
	black src/ tests/
	isort src/ tests/

format-check: ## Verifica formatação sem fazer mudanças
	black src/ tests/ --check
	isort src/ tests/ --check-only

clean: ## Remove arquivos temporários e cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .env
	@echo "$(GREEN)✓ Limpeza concluída$(NC)"

# Comandos de carga rápida

run-quick: ## Executa modo Insert Simples (args: JSON_PATH TABLE_NAME)
	$(PYTHON) -m src.json_to_mysql_quick \
		--json-path $(JSON_PATH) \
		--table $(TABLE_NAME) \
		--lines \
		--chunksize $(CHUNKSIZE) \
		--if-exists append

run-quick-replace: ## Insert Simples com --if-exists replace
	$(PYTHON) -m src.json_to_mysql_quick \
		--json-path $(JSON_PATH) \
		--table $(TABLE_NAME) \
		--lines \
		--if-exists replace

run-load: ## Executa modo LOAD DATA (alta performance)
	$(PYTHON) -m src.json_to_mysql_load \
		--json-path $(JSON_PATH) \
		--table $(TABLE_NAME) \
		--lines \
		--chunksize 50000 \
		--if-exists append

run-load-replace: ## LOAD DATA com --if-exists replace
	$(PYTHON) -m src.json_to_mysql_load \
		--json-path $(JSON_PATH) \
		--table $(TABLE_NAME) \
		--lines \
		--chunksize 50000 \
		--if-exists replace

run-upsert: ## Executa modo UPSERT (args: JSON_PATH TABLE_NAME)
	$(PYTHON) -m src.json_to_mysql_upsert \
		--json-path $(JSON_PATH) \
		--table $(TABLE_NAME) \
		--key-cols id \
		--lines

run-sample: ## Testa com arquivo de exemplo
	$(PYTHON) -m src.json_to_mysql_quick \
		--json-path ./tests/sample_ndjson.json \
		--table teste_amostra \
		--lines \
		--if-exists replace \
		--debug

docs: ## Abre documentação no navegador
	@echo "Abrindo README.md..."
	@if command -v xdg-open > /dev/null; then xdg-open README.md; \
	elif command -v open > /dev/null; then open README.md; \
	else echo "Abra README.md manualmente"; fi

# Comandos de desenvolvimento

venv: ## Cria ambiente virtual (sem instalar pacotes)
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Ative com: source $(VENV)/bin/activate$(NC)"

freeze: ## Salva versões de pacotes atuais
	$(PIP) freeze > requirements-locked.txt
	@echo "$(GREEN)✓ Dependências salvas em requirements-locked.txt$(NC)"

update-deps: ## Atualiza dependências
	$(PIP) install --upgrade -r requirements.txt

docker-build: ## Cria imagem Docker (se Dockerfile existir)
	docker build -t json-mysql-bulk:latest .

docker-run: ## Executa container Docker
	docker run --env-file .env json-mysql-bulk:latest

check: test lint ## Executa testes e lint

all: clean install test lint ## Executa completo (clean, install, test, lint)

.DEFAULT_GOAL := help
