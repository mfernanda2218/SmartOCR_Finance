# ==============================================================================
# SmartOCR Finance — Makefile
# ==============================================================================
# Automação de tarefas comuns do projeto.
#
# Uso:
#   make install    → Instalar dependências
#   make test       → Rodar testes
#   make lint       → Verificar código com ruff
#   make format     → Formatar código com ruff
#   make run        → Executar o projeto
#   make clean      → Limpar arquivos temporários
#   make help       → Exibir esta ajuda
# ==============================================================================

.PHONY: install test lint format run clean help check all

# Variáveis
PYTHON = python
UV = uv
SRC_DIR = src
TEST_DIR = tests
APP_DIR = app

# ---- Instalação ----

install: ## Instalar dependências do projeto
	$(UV) pip install -e ".[dev,test]"

install-prod: ## Instalar apenas dependências de produção
	$(UV) pip install -e .

# ---- Qualidade de Código ----

lint: ## Verificar código com ruff
	$(UV) run ruff check $(SRC_DIR) $(APP_DIR) $(TEST_DIR)

format: ## Formatar código com ruff
	$(UV) run ruff format $(SRC_DIR) $(APP_DIR) $(TEST_DIR)

format-check: ## Verificar formatação sem alterar
	$(UV) run ruff format --check $(SRC_DIR) $(APP_DIR) $(TEST_DIR)

typecheck: ## Verificar tipos com mypy
	$(UV) run mypy $(SRC_DIR)

check: lint format-check typecheck ## Executar todas as verificações

# ---- Testes ----

test: ## Rodar testes com pytest
	$(UV) run pytest $(TEST_DIR) -v

test-cov: ## Rodar testes com cobertura
	$(UV) run pytest $(TEST_DIR) -v --cov=$(SRC_DIR) --cov-report=term-missing

# ---- Execução ----

run: ## Executar o projeto
	$(PYTHON) -m app.main

# ---- Limpeza ----

clean: ## Limpar arquivos temporários
	@echo Limpando arquivos temporários...
	@if exist __pycache__ rd /s /q __pycache__
	@if exist .pytest_cache rd /s /q .pytest_cache
	@if exist .ruff_cache rd /s /q .ruff_cache
	@if exist .mypy_cache rd /s /q .mypy_cache
	@if exist htmlcov rd /s /q htmlcov
	@if exist .coverage del /q .coverage
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@echo Limpeza concluída!

# ---- Ajuda ----

help: ## Exibir esta mensagem de ajuda
	@echo.
	@echo  SmartOCR Finance - Comandos disponíveis:
	@echo  ========================================
	@echo.
	@echo  make install       - Instalar dependências
	@echo  make install-prod  - Instalar dependências de produção
	@echo  make lint          - Verificar código com ruff
	@echo  make format        - Formatar código com ruff
	@echo  make format-check  - Verificar formatação
	@echo  make typecheck     - Verificar tipos com mypy
	@echo  make check         - Todas as verificações
	@echo  make test          - Rodar testes
	@echo  make test-cov      - Rodar testes com cobertura
	@echo  make run           - Executar o projeto
	@echo  make clean         - Limpar temporários
	@echo.

# Default
.DEFAULT_GOAL := help
