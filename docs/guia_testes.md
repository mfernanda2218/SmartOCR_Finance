# 🧪 Guia Completo de Testes - SmartOCR Finance

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Configuração do Ambiente](#configuração-do-ambiente)
3. [Bases de Dados para Testes](#bases-de-dados-para-testes)
4. [Testando Cada Módulo](#testando-cada-módulo)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Boas Práticas](#boas-práticas)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este guia fornece instruções detalhadas para testar cada módulo e funcionalidade do sistema SmartOCR Finance, incluindo configuração de bases de dados para testes.

### Estrutura do Sistema
```
SmartOCR Finance
├── src/
│   ├── api/              # API FastAPI
│   ├── models/           # Modelos de banco de dados
│   ├── ocr/              # Engine OCR
│   ├── parser/           # Parser de documentos
│   ├── preprocessing/    # Pré-processamento de imagens
│   ├── repositories/     # Repositórios de dados
│   ├── services/         # Serviços de negócio
│   └── validation/       # Validadores
├── app/                  # Aplicação FastAPI
├── tests/                # Suite de testes
└── frontend/             # Interface React
```

---

## 🛠️ Configuração do Ambiente

### 1. Instalação de Dependências

```bash
# Instalar dependências básicas
pip install -r requirements.txt

# Instalar dependências de teste
pip install pytest pytest-cov httpx pytest-asyncio python-multipart

# Verificar instalação
pytest --version
```

### 2. Configuração do pytest

O arquivo `pyproject.toml` já está configurado com:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short --cov=src --cov=app --cov-report=html --cov-report=term-missing"
```

### 3. Variáveis de Ambiente

Crie um arquivo `.env.test` para testes:

```bash
# .env.test
DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=DEBUG
ENVIRONMENT=test
OCR_ENGINE=easyocr
OCR_LANGUAGE=por
```

---

## 🗄️ Bases de Dados para Testes

### Opção 1: SQLite em Memória (Recomendado para Testes Rápidos)

**Vantagens:**
- Rápido e leve
- Isolamento total entre testes
- Sem necessidade de configuração externa

**Implementação:**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base

@pytest.fixture(scope="function")
def test_db():
    """Cria banco de dados em memória para cada teste"""
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
```

**Uso:**
```python
def test_meu_repositorio(test_db):
    repo = MeuRepositorio(test_db)
    # Seu teste aqui
```

### Opção 2: PostgreSQL de Teste (Recomendado para Testes de Integração)

**Vantagens:**
- Mais próximo do ambiente de produção
- Suporta todas as features do PostgreSQL
- Melhor para testes de performance

**Configuração:**
```bash
# Criar banco de teste
createdb smartocr_test

# Variável de ambiente
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/smartocr_test
```

**Implementação:**
```python
# tests/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base

@pytest.fixture(scope="function")
def test_db_postgres():
    """Cria banco PostgreSQL para testes"""
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://localhost/smartocr_test")
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.rollback()
    session.close()
    # Limpar tabelas (opcional)
    Base.metadata.drop_all(bind=engine)
```

### Opção 3: Docker com PostgreSQL (Recomendado para CI/CD)

**docker-compose.test.yml:**
```yaml
version: '3.8'

services:
  test_db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: smartocr_test
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user"]
      interval: 5s
      timeout: 5s
      retries: 5
```

**Uso:**
```bash
# Iniciar banco de teste
docker-compose -f docker-compose.test.yml up -d

# Executar testes
export TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5433/smartocr_test
pytest tests/

# Parar banco
docker-compose -f docker-compose.test.yml down
```

---

## 🧪 Testando Cada Módulo

### 1. Testando Models (Modelos de Banco de Dados)

**Objetivo:** Validar a estrutura e comportamento dos modelos ORM.

**Exemplo:**
```python
# tests/test_models.py
import pytest
from datetime import datetime
from src.models.extraction_record import ExtractionRecord, DocumentType, ProcessingStatus

def test_extraction_record_creation(test_db):
    """Testa criação de registro de extração"""
    record = ExtractionRecord(
        filename="teste.png",
        file_size=1024,
        document_type=DocumentType.BOLETO,
        processing_status=ProcessingStatus.SUCCESS,
        processing_time_ms=1500,
        confidence_score=0.95,
        raw_text="Texto de teste",
        cpfs='["123.456.789-00"]',
        cnpjs='[]',
        dates='["15/09/2026"]',
        values='["100.00"]',
        boleto_lines='[]'
    )
    
    test_db.add(record)
    test_db.commit()
    
    # Validar
    assert record.id is not None
    assert record.filename == "teste.png"
    assert record.document_type == DocumentType.BOLETO
    assert record.processing_status == ProcessingStatus.SUCCESS

def test_extraction_record_to_dict(test_db):
    """Testa conversão para dicionário"""
    record = ExtractionRecord(
        filename="teste.png",
        raw_text="Texto"
    )
    test_db.add(record)
    test_db.commit()
    
    data = record.to_dict()
    assert "id" in data
    assert "filename" in data
    assert data["filename"] == "teste.png"
```

**Como testar:**
```bash
pytest tests/test_models.py -v
```

### 2. Testando Repositories (Repositórios de Dados)

**Objetivo:** Validar operações CRUD e consultas complexas.

**Exemplo:**
```python
# tests/test_repositories.py
import pytest
import json
from src.repositories.extraction_repository import ExtractionRepository

def test_repository_save(test_db):
    """Testa salvamento de registro"""
    repo = ExtractionRepository(test_db)
    
    record = repo.save(
        filename="teste.png",
        raw_text="CPF: 123.456.789-00",
        cpfs=["123.456.789-00"],
        cnpjs=[],
        dates=["15/09/2026"],
        values=["100.00"],
        boleto_lines=[]
    )
    
    assert record.id is not None
    assert record.filename == "teste.png"

def test_repository_get_by_id(test_db):
    """Testa busca por ID"""
    repo = ExtractionRepository(test_db)
    
    # Criar registro
    created = repo.save("teste.png", "Texto", [], [], [], [], [])
    
    # Buscar
    found = repo.get_by_id(created.id)
    
    assert found is not None
    assert found.id == created.id

def test_repository_get_all(test_db):
    """Testa busca de todos os registros"""
    repo = ExtractionRepository(test_db)
    
    # Criar múltiplos registros
    repo.save("a.png", "Texto A", [], [], [], [], [])
    repo.save("b.png", "Texto B", [], [], [], [], [])
    
    # Buscar todos
    records = repo.get_all()
    
    assert len(records) == 2

def test_repository_pagination(test_db):
    """Testa paginação"""
    repo = ExtractionRepository(test_db)
    
    # Criar 10 registros
    for i in range(10):
        repo.save(f"file{i}.png", f"Texto {i}", [], [], [], [], [])
    
    # Testar paginação
    page1 = repo.get_all(skip=0, limit=5)
    page2 = repo.get_all(skip=5, limit=5)
    
    assert len(page1) == 5
    assert len(page2) == 5
    assert len(set(r.id for r in page1 + page2)) == 10  # Sem duplicatas

def test_repository_delete(test_db):
    """Testa deleção"""
    repo = ExtractionRepository(test_db)
    
    # Criar registro
    record = repo.save("delete.png", "Texto", [], [], [], [], [])
    
    # Deletar
    result = repo.delete(record.id)
    
    assert result is True
    assert repo.get_by_id(record.id) is None
```

**Como testar:**
```bash
pytest tests/test_repositories.py -v
```

### 3. Testando OCR Engine

**Objetivo:** Validar extração de texto de imagens.

**Exemplo:**
```python
# tests/test_ocr_engine.py
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from src.ocr.engine import OCREngine

@pytest.fixture
def mock_easyocr():
    """Mock do EasyOCR para evitar downloads"""
    with patch("src.ocr.engine.easyocr.Reader") as mock_reader:
        instance = MagicMock()
        mock_reader.return_value = instance
        instance.readtext.return_value = [
            ([[10, 10], [100, 10], [100, 30], [10, 30]], "VALOR TOTAL", 0.98),
            ([[10, 40], [100, 40], [100, 60], [10, 60]], "R$ 150,00", 0.95),
        ]
        yield mock_reader, instance

def test_ocr_extract_text(mock_easyocr):
    """Testa extração de texto"""
    _, reader = mock_easyocr
    engine = OCREngine()
    
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    results = engine.extract_text(dummy_image, detail=1)
    
    assert len(results) == 2
    bbox, text, conf = results[0]
    assert text == "VALOR TOTAL"
    assert conf == 0.98

def test_ocr_get_full_text(mock_easyocr):
    """Testa obtenção de texto completo"""
    _, reader = mock_easyocr
    reader.readtext.return_value = ["LINHA 1", "LINHA 2", "LINHA 3"]
    
    engine = OCREngine()
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    full_text = engine.get_full_text(dummy_image, separator="\n")
    assert full_text == "LINHA 1\nLINHA 2\nLINHA 3"
```

**Como testar:**
```bash
pytest tests/test_ocr_engine.py -v
```

### 4. Testando Document Parser

**Objetivo:** Validar extração de campos específicos (CPF, CNPJ, datas, valores).

**Exemplo:**
```python
# tests/test_document_parser.py
import pytest
from src.parser.document_parser import DocumentParser

def test_extract_cpfs():
    """Testa extração de CPFs"""
    text = "CPF: 123.456.789-00 e outro CPF 987.654.321-00"
    cpfs = DocumentParser.extract_cpfs(text)
    
    assert "123.456.789-00" in cpfs
    assert "987.654.321-00" in cpfs
    assert len(cpfs) == 2

def test_extract_cnpjs():
    """Testa extração de CNPJs"""
    text = "CNPJ: 12.345.678/0001-90"
    cnpjs = DocumentParser.extract_cnpjs(text)
    
    assert "12.345.678/0001-90" in cnpjs

def test_extract_dates():
    """Testa extração de datas"""
    text = "Vencimento: 15/09/2026 e Data: 20/10/2026"
    dates = DocumentParser.extract_dates(text)
    
    assert "15/09/2026" in dates
    assert "20/10/2026" in dates

def test_extract_values():
    """Testa extração de valores monetários"""
    text = "Valor: R$ 1.250,00 e Total: R$ 500,00"
    values = DocumentParser.extract_monetary_values(text)
    
    assert "1.250,00" in values
    assert "500,00" in values

def test_extract_all():
    """Testa extração completa"""
    text = """
    CPF: 123.456.789-00
    CNPJ: 12.345.678/0001-90
    Vencimento: 15/09/2026
    Valor: R$ 1.250,00
    """
    
    result = DocumentParser.extract_all(text)
    
    assert "123.456.789-00" in result["cpfs"]
    assert "12.345.678/0001-90" in result["cnpjs"]
    assert "15/09/2026" in result["dates"]
    assert "1.250,00" in result["values"]
```

**Como testar:**
```bash
pytest tests/test_document_parser.py -v
```

### 5. Testando Validadores

**Objetivo:** Validar lógica de validação de documentos.

**Exemplo:**
```python
# tests/test_validators.py
import pytest
from src.validation.validators import DocumentValidator

def test_validate_cpf_valid():
    """Testa validação de CPF válido"""
    assert DocumentValidator.validate_cpf("529.982.247-25") is True
    assert DocumentValidator.validate_cpf("52998224725") is True

def test_validate_cpf_invalid():
    """Testa validação de CPF inválido"""
    assert DocumentValidator.validate_cpf("111.111.111-11") is False
    assert DocumentValidator.validate_cpf("123.456.789-00") is False

def test_validate_cnpj_valid():
    """Testa validação de CNPJ válido"""
    assert DocumentValidator.validate_cnpj("11.444.777/0001-61") is True
    assert DocumentValidator.validate_cnpj("11444777000161") is True

def test_validate_cnpj_invalid():
    """Testa validação de CNPJ inválido"""
    assert DocumentValidator.validate_cnpj("11.111.111/1111-11") is False
```

**Como testar:**
```bash
pytest tests/test_validators.py -v
```

### 6. Testando API FastAPI

**Objetivo:** Validar endpoints da API.

**Exemplo:**
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import numpy as np
import cv2

client = TestClient(app)

def test_root_endpoint():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "project" in response.json()

def test_health_check():
    """Testa health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_extract_endpoint_no_file():
    """Testa extração sem arquivo"""
    response = client.post("/api/v1/extract")
    assert response.status_code == 422  # Unprocessable Entity

def test_extract_endpoint_success():
    """Testa extração com sucesso"""
    # Criar imagem dummy
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", img)
    dummy_image = encoded.tobytes()
    
    # Mock do serviço OCR
    from unittest.mock import patch
    with patch("src.services.ocr_service.OCRService") as mock_service:
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        mock_instance.process_image.return_value = {
            "cpfs": ["123.456.789-00"],
            "cnpjs": [],
            "dates": ["15/09/2026"],
            "values": ["100.00"],
            "boleto_lines": [],
            "raw_text": "Texto mock",
            "metadata": {
                "document_type": "boleto",
                "processing_status": "success",
                "confidence_score": 0.95,
                "processing_time_ms": 100
            }
        }
        
        from app.main import app
        app.dependency_overrides[mock_service] = mock_instance
        
        try:
            response = client.post(
                "/api/v1/extract",
                files={"file": ("test.png", dummy_image, "image/png")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "cpfs" in data
            assert "123.456.789-00" in data["cpfs"]
        finally:
            app.dependency_overrides.clear()
```

**Como testar:**
```bash
pytest tests/test_api.py -v
```

### 7. Testando Serviços de Negócio

**Objetivo:** Validar lógica de negócio e orquestração.

**Exemplo:**
```python
# tests/test_ocr_service.py
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch
from src.services.ocr_service import OCRService

@pytest.fixture
def mock_ocr_service():
    """Mock do serviço OCR"""
    with patch("src.services.ocr_service.OCREngine") as mock_engine:
        instance = MagicMock()
        mock_engine.return_value = instance
        instance.get_full_text.return_value = "CPF: 123.456.789-00\nValor: R$ 100,00"
        yield mock_engine, instance

def test_ocr_service_process_image(mock_ocr_service, test_db):
    """Testa processamento completo de imagem"""
    _, engine = mock_ocr_service
    service = OCRService()
    
    # Criar imagem dummy
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", img)
    image_bytes = encoded.tobytes()
    
    # Processar
    result = service.process_image(image_bytes, filename="test.png", db=test_db)
    
    # Validar resultado
    assert "cpfs" in result
    assert "raw_text" in result
    assert "123.456.789-00" in result["cpfs"]
    
    # Validar persistência
    from src.repositories.extraction_repository import ExtractionRepository
    repo = ExtractionRepository(test_db)
    records = repo.get_all()
    assert len(records) > 0
```

**Como testar:**
```bash
pytest tests/test_ocr_service.py -v
```

---

## 📚 Exemplos Práticos

### Exemplo 1: Teste Completo de Fluxo OCR

```python
# tests/test_ocr_flow.py
import pytest
import numpy as np
import cv2
from unittest.mock import patch
from src.services.ocr_service import OCRService
from src.repositories.extraction_repository import ExtractionRepository

def test_complete_ocr_flow(test_db):
    """Testa fluxo completo: upload -> OCR -> persistência -> recuperação"""
    
    # 1. Setup
    service = OCRService()
    repo = ExtractionRepository(test_db)
    
    # 2. Criar imagem de teste
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    cv2.putText(img, "CPF: 123.456.789-00", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, "Valor: R$ 1.250,00", (10, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    _, encoded = cv2.imencode(".png", img)
    image_bytes = encoded.tobytes()
    
    # 3. Processar imagem
    result = service.process_image(image_bytes, filename="teste.png", db=test_db)
    
    # 4. Validar extração
    assert "cpfs" in result
    assert "values" in result
    assert "raw_text" in result
    
    # 5. Validar persistência
    records = repo.get_all()
    assert len(records) == 1
    
    saved_record = records[0]
    assert saved_record.filename == "teste.png"
    assert saved_record.processing_status.value == "success"
    
    # 6. Validar recuperação
    recovered = repo.get_by_id(saved_record.id)
    assert recovered is not None
    assert recovered.id == saved_record.id
```

### Exemplo 2: Teste com Dados Reais

```python
# tests/test_real_data.py
import pytest
from pathlib import Path

def test_with_real_boleto(test_db):
    """Testa com imagem de boleto real"""
    
    # Caminho para imagem real
    boleto_path = Path("data/samples/boleto_real.png")
    
    if not boleto_path.exists():
        pytest.skip("Imagem de teste não encontrada")
    
    # Ler imagem
    with open(boleto_path, "rb") as f:
        image_bytes = f.read()
    
    # Processar
    from src.services.ocr_service import OCRService
    service = OCRService()
    result = service.process_image(image_bytes, filename="boleto_real.png", db=test_db)
    
    # Validar resultados esperados para este boleto específico
    assert len(result["cpfs"]) > 0 or len(result["cnpjs"]) > 0
    assert len(result["values"]) > 0
    assert len(result["dates"]) > 0
```

### Exemplo 3: Teste de Performance

```python
# tests/test_performance_specific.py
import pytest
import time
import numpy as np
import cv2

def test_ocr_performance_limit(test_db):
    """Valida que OCR processa em tempo aceitável"""
    from src.services.ocr_service import OCRService
    
    service = OCRService()
    
    # Criar imagem
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", img)
    image_bytes = encoded.tobytes()
    
    # Medir tempo
    start_time = time.time()
    result = service.process_image(image_bytes, db=test_db)
    elapsed_time = time.time() - start_time
    
    # Validar limite
    assert elapsed_time < 10, f"OCR demorou {elapsed_time:.2f}s (limite: 10s)"
    assert "cpfs" in result
```

---

## ✅ Boas Práticas

### 1. Organização de Testes

```python
# Estrutura recomendada
tests/
├── unit/              # Testes unitários isolados
│   ├── test_models.py
│   ├── test_validators.py
│   └── test_parser.py
├── integration/       # Testes de integração
│   ├── test_repository.py
│   ├── test_ocr_service.py
│   └── test_api.py
├── e2e/              # Testes end-to-end
│   └── test_complete_flow.py
└── performance/      # Testes de performance
    └── test_benchmarks.py
```

### 2. Nomenclatura de Testes

```python
# Padronização: test_<modulo>_<funcionalidade>_<cenario>_<resultado>

def test_repository_save_success():              # ✅ Bom
def test_repository_save():                      # ⚠️ Poderia ser mais específico
def test_save():                                 # ❌ Muito genérico
def test_repository_save_with_invalid_data():    # ✅ Bom
```

### 3. AAA Pattern (Arrange, Act, Assert)

```python
def test_user_creation(test_db):
    # Arrange (Preparação)
    user_data = {
        "name": "João Silva",
        "email": "joao@example.com"
    }
    
    # Act (Ação)
    user = create_user(user_data)
    
    # Assert (Verificação)
    assert user.id is not None
    assert user.name == "João Silva"
    assert user.email == "joao@example.com"
```

### 4. Isolamento de Testes

```python
# Cada teste deve ser independente
def test_a(test_db):
    repo.save("a.png", "Texto A")
    # Não deve depender de test_b

def test_b(test_db):
    # Deve funcionar mesmo se test_a falhar
    repo.save("b.png", "Texto B")
```

### 5. Mocks vs Testes Reais

```python
# Use mocks para dependências externas
def test_with_mock_ocr():
    with patch("src.ocr.engine.easyocr.Reader") as mock:
        mock.return_value = MagicMock()
        # Teste com mock

# Use testes reais para lógica interna
def test_parser_logic():
    text = "CPF: 123.456.789-00"
    result = parse_cpf(text)  # Lógica interna, sem mock
```

---

## 🔧 Troubleshooting

### Problema 1: Erro de Importação

**Erro:**
```
ModuleNotFoundError: No module named 'src'
```

**Solução:**
```bash
# Verificar pythonpath
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou executar do diretório raiz
cd /path/to/SmartOCR_Finance
pytest tests/
```

### Problema 2: Banco de Dados em Uso

**Erro:**
```
sqlalchemy.exc.OperationalError: database is locked
```

**Solução:**
```python
# Usar banco em memória para cada teste
@pytest.fixture(scope="function")
def test_db():
    # Cada teste tem seu próprio banco
    ...
```

### Problema 3: Testes Lentos

**Solução:**
```bash
# Executar apenas testes específicos
pytest tests/test_unit/ -v

# Usar paralelização (instalar pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto

# Desativar cobertura para velocidade
pytest tests/ -v --no-cov
```

### Problema 4: Mocks Não Funcionando

**Erro:**
```
AttributeError: Mock object has no attribute 'method'
```

**Solução:**
```python
# Configurar mock corretamente
mock_instance = MagicMock()
mock_instance.method.return_value = "expected_value"

# Ou usar autospec
with patch('module.Class', autospec=True) as mock:
    mock.return_value = MagicMock()
```

### Problema 5: Imagens de Teste

**Solução:**
```python
# Criar fixtures de imagens
@pytest.fixture
def sample_image():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", img)
    return encoded.tobytes()

# Ou usar imagens reais
@pytest.fixture
def real_boleto():
    path = Path("data/samples/boleto.png")
    if path.exists():
        return path.read_bytes()
    pytest.skip("Imagem não encontrada")
```

---

## 🚀 Scripts Úteis

### Script para Executar Testes Específicos

```bash
#!/bin/bash
# scripts/test_module.sh

MODULE=$1

if [ -z "$MODULE" ]; then
    echo "Uso: ./test_module.sh <nome_do_modulo>"
    echo "Exemplo: ./test_module.sh repository"
    exit 1
fi

pytest tests/test_${MODULE}.py -v --tb=short
```

### Script para Testar com Banco PostgreSQL

```bash
#!/bin/bash
# scripts/test_with_postgres.sh

export TEST_DATABASE_URL="postgresql://user:password@localhost:5432/smartocr_test"
pytest tests/ -v --tb=short
```

### Script para Limpar Banco de Teste

```bash
#!/bin/bash
# scripts/clean_test_db.sh

# SQLite
rm -f test.db

# PostgreSQL
psql -U user -d smartocr_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

---

## 📖 Recursos Adicionais

### Documentação Oficial
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/persistence_techniques.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

### Tutoriais
- [Effective Python Testing with Pytest](https://realpython.com/pytest-python-test-coverage/)
- [Database Testing Best Practices](https://www.testautomationguru.com/database-testing-best-practices/)

### Ferramentas
- **pytest-cov**: Cobertura de código
- **pytest-xdist**: Execução paralela
- **pytest-mock**: Mocks avançados
- **factory-boy**: Criação de dados de teste

---

## 🎯 Checklist para Começar a Testar

- [ ] Configurar ambiente de testes
- [ ] Escolher tipo de banco de dados para testes
- [ ] Criar fixtures básicas no conftest.py
- [ ] Escrever primeiro teste unitário simples
- [ ] Executar teste e verificar resultado
- [ ] Adicionar mais testes gradualmente
- [ ] Configurar cobertura de código
- [ ] Integrar com workflow de desenvolvimento

Este guia fornece uma base sólida para começar a testar o sistema SmartOCR Finance. Comece com testes simples e vá aumentando a complexidade gradualmente!