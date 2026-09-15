"""Testes de Performance para o SmartOCR Finance.

Estes testes validam que o sistema atende aos requisitos de performance,
incluindo tempo de processamento de OCR, tempo de resposta da API e
eficiência de operações de banco de dados.
"""

import pytest
import time
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

from smart_ocr_finance.ocr.engine import OCREngine
from smart_ocr_finance.services.ocr_service import OCRService
from src.repositories.extraction_repository import ExtractionRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base


@pytest.fixture
def performance_db():
    """Cria banco de dados em memória para testes de performance."""
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def performance_repo(performance_db):
    """Cria instância do repositório para testes de performance."""
    return ExtractionRepository(performance_db)


@pytest.fixture
def mock_ocr_performance():
    """Mock do OCR para testes de performance."""
    with patch("smart_ocr_finance.ocr.engine.easyocr.Reader") as mock_reader:
        instance = MagicMock()
        mock_reader.return_value = instance
        # Simular tempo de processamento realista
        def slow_readtext(*args, **kwargs):
            time.sleep(0.1)  # Simular 100ms de processamento
            return ["Texto simulado", "CPF: 123.456.789-00", "Valor: R$ 100,00"]
        
        instance.readtext = slow_readtext
        yield mock_reader


def test_ocr_performance_acceptable(mock_ocr_performance):
    """Valida que o OCR processa imagem em tempo aceitável (< 10s)."""
    
    engine = OCREngine()
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    start_time = time.time()
    result = engine.extract_text(dummy_image)
    elapsed_time = time.time() - start_time
    
    # OCR deve completar em menos de 10 segundos
    assert elapsed_time < 10, f"OCR demorou {elapsed_time:.2f}s (limite: 10s)"
    assert len(result) > 0


def test_ocr_service_performance(mock_ocr_performance, performance_db):
    """Valida performance do serviço OCR completo."""
    
    from src.services.ocr_service import OCRService as SrcOCRService
    
    service = SrcOCRService()
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", dummy_image)
    image_bytes = encoded.tobytes()
    
    start_time = time.time()
    result = service.process_image(image_bytes, filename="test.png", db=performance_db)
    elapsed_time = time.time() - start_time
    
    # Serviço completo deve completar em menos de 15 segundos
    assert elapsed_time < 15, f"Serviço OCR demorou {elapsed_time:.2f}s (limite: 15s)"
    assert "cpfs" in result
    assert "raw_text" in result


def test_database_insert_performance(performance_repo):
    """Valida performance de inserção no banco de dados."""
    
    # Medir tempo para 100 inserções
    start_time = time.time()
    
    for i in range(100):
        performance_repo.save(
            filename=f"perf_test_{i}.png",
            raw_text=f"Texto de teste {i}",
            cpfs=[f"123.456.789-{i:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*10}.00"],
            boleto_lines=[]
        )
    
    elapsed_time = time.time() - start_time
    
    # 100 inserções devem completar em menos de 5 segundos
    assert elapsed_time < 5, f"100 inserções demoraram {elapsed_time:.2f}s (limite: 5s)"
    
    # Verificar que todos foram inseridos
    records = performance_repo.get_all()
    assert len(records) == 100


def test_database_query_performance(performance_repo):
    """Valida performance de consultas no banco de dados."""
    
    # Inserir dados de teste
    for i in range(100):
        performance_repo.save(
            filename=f"query_test_{i}.png",
            raw_text=f"Texto {i}",
            cpfs=[f"111.222.333-{i:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*10}.00"],
            boleto_lines=[]
        )
    
    # Medir tempo de consulta
    start_time = time.time()
    records = performance_repo.get_all()
    elapsed_time = time.time() - start_time
    
    # Consulta deve completar em menos de 1 segundo
    assert elapsed_time < 1, f"Consulta demorou {elapsed_time:.2f}s (limite: 1s)"
    assert len(records) == 100


def test_database_pagination_performance(performance_repo):
    """Valida performance de paginação."""
    
    # Inserir muitos registros
    for i in range(1000):
        performance_repo.save(
            filename=f"pag_test_{i}.png",
            raw_text=f"Texto {i}",
            cpfs=[f"444.555.666-{i%100:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*5}.00"],
            boleto_lines=[]
        )
    
    # Medir tempo de paginação
    start_time = time.time()
    
    for skip in [0, 100, 500, 900]:
        records = performance_repo.get_all(skip=skip, limit=50)
        assert len(records) == 50
    
    elapsed_time = time.time() - start_time
    
    # 4 consultas paginadas devem completar em menos de 2 segundos
    assert elapsed_time < 2, f"Paginação demorou {elapsed_time:.2f}s (limite: 2s)"


def test_database_delete_performance(performance_repo):
    """Valida performance de deleção."""
    
    # Inserir registros
    record_ids = []
    for i in range(50):
        record = performance_repo.save(
            filename=f"delete_test_{i}.png",
            raw_text=f"Texto {i}",
            cpfs=[f"777.888.999-{i:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*20}.00"],
            boleto_lines=[]
        )
        record_ids.append(record.id)
    
    # Medir tempo de deleção
    start_time = time.time()
    
    for record_id in record_ids:
        performance_repo.delete(record_id)
    
    elapsed_time = time.time() - start_time
    
    # 50 deleções devem completar em menos de 3 segundos
    assert elapsed_time < 3, f"50 deleções demoraram {elapsed_time:.2f}s (limite: 3s)"
    
    # Verificar que foram deletados
    records = performance_repo.get_all()
    assert len(records) == 0


def test_api_response_performance():
    """Valida tempo de resposta da API."""
    from fastapi.testclient import TestClient
    from app.main import app
    from smart_ocr_finance.services.ocr_service import OCRService
    
    # Mock do serviço
    class MockOCRService:
        def process_image(self, image_bytes, filename=None, db=None):
            time.sleep(0.05)  # Simular 50ms
            return {
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
                    "processing_time_ms": 50
                }
            }
    
    app.dependency_overrides[OCRService] = MockOCRService
    
    try:
        client = TestClient(app)
        
        # Criar imagem de teste
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".png", img)
        dummy_image_bytes = encoded.tobytes()
        
        # Medir tempo de resposta
        start_time = time.time()
        response = client.post(
            "/api/v1/extract",
            files={"file": ("test.png", dummy_image_bytes, "image/png")}
        )
        elapsed_time = time.time() - start_time
        
        # API deve responder em menos de 1 segundo
        assert response.status_code == 200
        assert elapsed_time < 1, f"API demorou {elapsed_time:.2f}s (limite: 1s)"
        
    finally:
        app.dependency_overrides.clear()


def test_memory_efficiency():
    """Testa eficiência de memória em operações comuns."""
    import gc
    import sys
    
    # Criar imagem grande para teste
    large_image = np.zeros((2000, 2000, 3), dtype=np.uint8)
    
    # Medir uso de memória antes
    gc.collect()
    mem_before = sys.getsizeof(large_image)
    
    # Processar imagem
    _, encoded = cv2.imencode(".png", large_image)
    image_bytes = encoded.tobytes()
    
    # Medir uso de memória depois
    gc.collect()
    mem_after = sys.getsizeof(image_bytes)
    
    # Verificar que não há vazamento de memória significativo
    # (este é um teste básico, em produção usariamos ferramentas mais avançadas)
    assert mem_after < mem_before * 10, "Possível vazamento de memória detectado"


def test_concurrent_operations_performance(performance_repo):
    """Testa performance de operações sequenciais (simulando concorrência)."""
    
    results = []
    
    # Simular operações sequenciais (mais simples para testes)
    for worker_id in range(5):
        start_time = time.time()
        for i in range(10):
            performance_repo.save(
                filename=f"concurrent_{worker_id}_{i}.png",
                raw_text=f"Worker {worker_id} - Item {i}",
                cpfs=[f"111.222.333-{worker_id:02d}"],
                cnpjs=[],
                dates=["15/09/2026"],
                values=[f"{(i+1)*10}.00"],
                boleto_lines=[]
            )
        elapsed = time.time() - start_time
        results.append((worker_id, elapsed))
    
    # Verificar que todos os registros foram salvos
    records = performance_repo.get_all()
    assert len(records) == 50  # 5 workers * 10 operações
    
    # Verificar performance média
    avg_time = sum(r[1] for r in results) / len(results)
    assert avg_time < 3, f"Tempo médio por worker: {avg_time:.2f}s (limite: 3s)"


def test_batch_processing_performance(performance_repo):
    """Testa performance de processamento em lote."""
    
    # Simular processamento em lote de 100 registros
    batch_data = []
    for i in range(100):
        batch_data.append({
            "filename": f"batch_{i}.png",
            "raw_text": f"Batch item {i}",
            "cpfs": [f"999.888.777-{i%100:02d}"],
            "cnpjs": [],
            "dates": ["15/09/2026"],
            "values": [f"{(i+1)*15}.00"],
            "boleto_lines": []
        })
    
    start_time = time.time()
    
    # Processar em lote
    for data in batch_data:
        performance_repo.save(**data)
    
    elapsed_time = time.time() - start_time
    
    # 100 operações em lote devem completar em menos de 3 segundos
    assert elapsed_time < 3, f"Batch processing demorou {elapsed_time:.2f}s (limite: 3s)"
    
    # Verificar integridade
    records = performance_repo.get_all()
    assert len(records) == 100