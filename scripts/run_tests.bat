@echo off
REM Script para executar todos os testes do projeto SmartOCR Finance (Windows)

echo 🧪 Executando testes do SmartOCR Finance...
echo.

REM Verificar se estamos no diretório correto
if not exist "pyproject.toml" (
    echo ❌ Erro: pyproject.toml não encontrado. Execute este script no diretório raiz do projeto.
    exit /b 1
)

REM Executar testes com cobertura
echo 📊 Executando testes com cobertura de código...
pytest tests/ -v --tb=short --cov=src --cov=app --cov-report=html --cov-report=term-missing

REM Verificar resultado
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Todos os testes passaram!
    echo 📈 Relatório de cobertura gerado em htmlcov/index.html
) else (
    echo.
    echo ❌ Alguns testes falharam. Verifique o output acima.
    exit /b 1
)