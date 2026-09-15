#!/bin/bash
# Script para executar todos os testes do projeto SmartOCR Finance

echo "🧪 Executando testes do SmartOCR Finance..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Erro: pyproject.toml não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Executar testes com cobertura
echo "📊 Executando testes com cobertura de código..."
pytest tests/ -v --tb=short --cov=src --cov=app --cov-report=html --cov-report=term-missing

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Todos os testes passaram!"
    echo "📈 Relatório de cobertura gerado em htmlcov/index.html"
else
    echo ""
    echo "❌ Alguns testes falharam. Verifique o output acima."
    exit 1
fi