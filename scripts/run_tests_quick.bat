@echo off
REM Script para executar testes rápidos (sem cobertura)

echo 🧪 Executando testes rápidos...
echo.

pytest tests/ -v --tb=short

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Testes rápidos concluídos com sucesso!
) else (
    echo.
    echo ❌ Alguns testes falharam.
    exit /b 1
)