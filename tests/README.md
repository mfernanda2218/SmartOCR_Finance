# 🧪 Guia Rápido de Testes - SmartOCR Finance

## 🚀 Começando Rápido

### Executar Todos os Testes
```bash
# Com cobertura
pytest tests/ -v --tb=short --cov=src --cov=app --cov-report=html

# Sem cobertura (mais rápido)
pytest tests/ -v --tb=short

# Usar scripts
./scripts/run_tests.sh          # Linux/Mac
scripts\run_tests.bat           # Windows
```

### Executar Testes Específicos
```bash
# Testar um módulo específico
pytest tests/test_repository.py -v

# Testar uma classe específica
pytest tests/test_repository.py::TestRepositoryCRUD -v

# Testar um método específico
pytest tests/test_repository.py::TestRepositoryCRUD::test_save -v

# Testar por palavra-chave
pytest tests/ -k "cpf" -v
```

---

## 🗄️ Configuração de Banco de Dados

### Opção 1: SQLite em Memória (Padrão)
```bash
# Não precisa de configuração
pytest tests/ -v
```

### Opção 2: PostgreSQL Local
```bash
# Criar banco
createdb smartocr_test

# Configurar variável de ambiente
export TEST_DATABASE_URL="postgresql://usuario:senha@localhost:5432/smartocr_test"

# Executar testes
pytest tests/ -v
```

### Opção 3: PostgreSQL com Docker
```bash
# Iniciar container
docker run -d --name smartocr-test-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=smartocr_test \
  -p 5433:5432 \
  postgres:15-alpine

# Configurar variável
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smartocr_test"

# Executar testes
pytest tests/ -v

# Parar container
docker stop smartocr-test-db
docker rm smartocr-test-db
```

---

## 📚 Estrutura de Testes

```
tests/
├── conftest.py                  # Fixtures compartilhadas
├── test_template.py             # Template para novos testes
├── test_postgres_example.py     # Exemplos com PostgreSQL
├── test_api.py                  # Testes da API
├── test_config.py               # Testes de configuração
├── test_document_parser.py      # Testes do parser
├── test_e2e.py                  # Testes end-to-end
├── test_image_loader.py         # Testes de carregamento
├── test_integration.py          # Testes de integração
├── test_ocr_engine.py           # Testes do OCR
├── test_performance.py          # Testes de performance
├── test_processor.py            # Testes de processamento
├── test_repository.py           # Testes do repositório
└── test_validators.py           # Testes de validadores
```

---

## 🎯 Testando Cada Módulo

### 1. Models (Modelos de Dados)
```bash
pytest tests/ -k "model" -v
```

### 2. Repositories (Repositórios)
```bash
pytest tests/test_repository.py -v
```

### 3. OCR Engine
```bash
pytest tests/test_ocr_engine.py -v
```

### 4. Document Parser
```bash
pytest tests/test_document_parser.py -v
```

### 5. Validadores
```bash
pytest tests/test_validators.py -v
```

### 6. API
```bash
pytest tests/test_api.py -v
```

### 7. Serviços
```bash
pytest tests/ -k "service" -v
```

---

## 📖 Exemplos Práticos

### Criar Novo Teste
```bash
# Copiar template
cp tests/test_template.py tests/test_meu_modulo.py

# Editar e implementar testes
# vim tests/test_meu_modulo.py

# Executar
pytest tests/test_meu_modulo.py -v
```

### Testar com PostgreSQL
```bash
# Ver exemplos em
cat tests/test_postgres_example.py

# Executar
export TEST_DATABASE_URL="postgresql://user:pass@localhost:5432/test_db"
pytest tests/test_postgres_example.py -v
```

### Testar Performance
```bash
pytest tests/test_performance.py -v
```

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"
```bash
# Executar do diretório raiz
cd /path/to/SmartOCR_Finance
pytest tests/ -v
```

### Erro: "database is locked"
```bash
# Usar banco em memória (padrão)
pytest tests/ -v
```

### Testes muito lentos
```bash
# Sem cobertura
pytest tests/ -v --no-cov

# Apenas testes unitários
pytest tests/test_repository.py tests/test_validators.py -v

# Paralelização (requer pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

---

## 📊 Relatórios

### Cobertura de Código
```bash
# Gerar relatório HTML
pytest tests/ --cov=src --cov=app --cov-report=html

# Abrir relatório
# Linux/Mac
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Resultados Detalhados
```bash
# Verboso
pytest tests/ -vv

# Com traceback curto
pytest tests/ -v --tb=short

# Com traceback longo
pytest tests/ -v --tb=long
```

---

## 📚 Documentação Completa

Para documentação detalhada, consulte:
- [Guia Completo de Testes](../docs/guia_testes.md)
- [Documentação da Fase 12](../docs/fase_12_testes.md)

---

## 🎯 Checklist para Novos Testes

- [ ] Copiar `test_template.py`
- [ ] Implementar testes básicos
- [ ] Adicionar fixtures necessárias
- [ ] Testar com banco em memória
- [ ] Testar com PostgreSQL (opcional)
- [ ] Verificar cobertura
- [ ] Documentar testes complexos

---

## 💡 Dicas

1. **Comece simples**: Teste unitário primeiro, depois integração
2. **Use fixtures**: Reutilize setup no conftest.py
3. **Isolamento**: Cada teste deve ser independente
4. **AAA Pattern**: Arrange, Act, Assert
5. **Nomes descritivos**: `test_<modulo>_<funcionalidade>_<resultado>`

---

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique o [guia completo](../docs/guia_testes.md)
2. Consulte os [exemplos PostgreSQL](test_postgres_example.py)
3. Use o [template](test_template.py) como base