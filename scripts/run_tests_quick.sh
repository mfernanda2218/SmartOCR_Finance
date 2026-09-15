#!/bin/bash
# Script para executar testes rápidos (sem cobertura)

echo "🧪 Executando testes rápidos..."
echo ""

pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Testes rápidos concluídos com sucesso!"
else
    echo ""
    echo "❌ Alguns testes falharam."
    exit 1
fi