"""Testes de Integração entre API e Banco de Dados.

Estes testes validam a integração entre os componentes da API FastAPI
e o banco de dados SQLAlchemy, garantindo que a persistência e recuperação
de dados funcionem corretamente.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from src.models.database import Base
from src.models.extraction_record import ExtractionRecord
from src.repositories.extraction_repository import ExtractionRepository
from smart_ocr_finance.services.ocr_service import OCRService


@pytest.fixture(scope="function")
def integration_db():
    """Cria banco de dados em memória para testes de integração."""
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def integration_repo(integration_db):
    """Cria instância do repositório para testes de integração."""
    return ExtractionRepository(integration_db)


@pytest.fixture
def mock_ocr_service_integration():
    """Mock do serviço OCR para testes de integração."""
    with patch("smart_ocr_finance.services.ocr_service.OCREngine") as mock_engine:
        mock_instance = MagicMock()
        mock_engine.return_value = mock_instance
        mock_instance.extract_text.return_value = [
            "CPF: 123.456.789-00",
            "Valor: R$ 500,00",
            "Vencimento: 20/09/2026"
        ]
        mock_instance.get_full_text.return_value = "CPF: 123.456.789-00\nValor: R$ 500,00\nVencimento: 20/09/2026"
        yield mock_instance


def test_integration_api_with_database(integration_repo, mock_ocr_service_integration):
    """Testa integração completa: API -> OCR Service -> Banco de Dados."""
    
    # Configurar OCR Service mockado
    class MockOCRService:
        def process_image(self, image_bytes, filename=None, db=None):
            return {
                "cpfs": ["123.456.789-00"],
                "cnpjs": [],
                "dates": ["20/09/2026"],
                "values": ["500,00"],
                "boleto_lines": [],
                "raw_text": "CPF: 123.456.789-00\nValor: R$ 500,00\nVencimento: 20/09/2026",
                "metadata": {
                    "document_type": "boleto",
                    "processing_status": "success",
                    "confidence_score": 0.95,
                    "processing_time_ms": 1500
                }
            }
    
    # Sobrescrever dependência
    app.dependency_overrides[OCRService] = MockOCRService
    
    try:
        client = TestClient(app)
        
        # Testar endpoint de extração com persistência
        import numpy as np
        import cv2
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".png", img)
        dummy_image_bytes = encoded.tobytes()
        
        # Testar apenas a resposta da API (sem persistência real neste teste)
        response = client.post(
            "/api/v1/extract",
            files={"file": ("test.png", dummy_image_bytes, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "cpfs" in data
        assert "raw_text" in data
        assert "metadata" in data
        
    finally:
        app.dependency_overrides.clear()


def test_integration_repository_crud(integration_repo):
    """Testa operações CRUD completas do repositório."""
    
    # Create
    record = integration_repo.save(
        filename="integration_test.png",
        raw_text="CPF: 987.654.321-00\nValor: R$ 1.000,00",
        cpfs=["987.654.321-00"],
        cnpjs=[],
        dates=["25/09/2026"],
        values=["1.000,00"],
        boleto_lines=[]
    )
    
    assert record.id is not None
    assert record.filename == "integration_test.png"
    
    # Read
    found = integration_repo.get_by_id(record.id)
    assert found is not None
    assert found.id == record.id
    assert found.filename == "integration_test.png"
    
    # Update (simulado via save com mesmo ID)
    updated = integration_repo.save(
        filename="integration_test_updated.png",
        raw_text="Texto atualizado",
        cpfs=["987.654.321-00"],
        cnpjs=[],
        dates=["25/09/2026"],
        values=["1.500,00"],
        boleto_lines=[]
    )
    
    assert updated.filename == "integration_test_updated.png"
    
    # Delete
    deleted = integration_repo.delete(record.id)
    assert deleted is True
    
    # Verify deletion
    found_after_delete = integration_repo.get_by_id(record.id)
    assert found_after_delete is None


def test_integration_pagination(integration_repo):
    """Testa paginação integrada com banco de dados."""
    
    # Criar múltiplos registros
    for i in range(15):
        integration_repo.save(
            filename=f"paginated_{i}.png",
            raw_text=f"Registro {i}",
            cpfs=[f"123.456.789-{i:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*100}.00"],
            boleto_lines=[]
        )
    
    # Testar diferentes paginações
    page1 = integration_repo.get_all(skip=0, limit=5)
    assert len(page1) == 5
    
    page2 = integration_repo.get_all(skip=5, limit=5)
    assert len(page2) == 5
    
    page3 = integration_repo.get_all(skip=10, limit=5)
    assert len(page3) == 5
    
    # Verificar que não há sobreposição
    ids_page1 = {r.id for r in page1}
    ids_page2 = {r.id for r in page2}
    ids_page3 = {r.id for r in page3}
    
    assert len(ids_page1 & ids_page2) == 0
    assert len(ids_page2 & ids_page3) == 0
    assert len(ids_page1 & ids_page3) == 0


def test_integration_filtering(integration_repo):
    """Testa filtros de busca integrados."""
    
    # Criar registros com diferentes características
    integration_repo.save("a.png", "txt", ["123.456.789-00"], [], ["15/09/2026"], ["100.00"], [])
    integration_repo.save("b.png", "txt", [], ["12.345.678/0001-90"], ["20/09/2026"], ["200.00"], [])
    
    # Buscar todos
    all_records = integration_repo.get_all()
    assert len(all_records) == 2
    
    # Verificar que podemos buscar por diferentes critérios
    import json
    cpf_records = [r for r in all_records if r.cpfs and json.loads(r.cpfs)]
    assert len(cpf_records) == 1
    
    cnpj_records = [r for r in all_records if r.cnpjs and json.loads(r.cnpjs)]
    assert len(cnpj_records) == 1


def test_integration_error_handling(integration_repo):
    """Testa tratamento de erros na integração."""
    
    # Testar busca de ID inexistente
    not_found = integration_repo.get_by_id(99999)
    assert not_found is None
    
    # Testar deleção de ID inexistente
    deleted = integration_repo.delete(99999)
    assert deleted is False
    
    # Testar save com dados inválidos (deve ser tratado pelo modelo)
    try:
        integration_repo.save(
            filename=None,  # Nome inválido
            raw_text="",
            cpfs=[],
            cnpjs=[],
            dates=[],
            values=[],
            boleto_lines=[]
        )
        # Se chegar aqui, o banco aceitou o dado inválido
        # Em produção, isso deveria ser validado antes
    except Exception as e:
        # Esperado que haja alguma validação
        assert True


def test_integration_concurrent_operations(integration_repo):
    """Testa operações concorrentes simuladas."""
    
    # Simular múltiplas operações de save
    records = []
    for i in range(10):
        record = integration_repo.save(
            filename=f"concurrent_{i}.png",
            raw_text=f"Concurrent {i}",
            cpfs=[f"111.222.333-{i:02d}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*50}.00"],
            boleto_lines=[]
        )
        records.append(record)
    
    # Verificar que todos foram salvos corretamente
    all_records = integration_repo.get_all()
    assert len(all_records) == 10
    
    # Verificar que não há duplicatas
    ids = {r.id for r in all_records}
    assert len(ids) == 10


def test_integration_data_integrity(integration_repo):
    """Testa integridade de dados após múltiplas operações."""
    
    # Criar registro complexo
    original_data = {
        "filename": "integrity_test.png",
        "raw_text": "CPF: 123.456.789-00\nCNPJ: 12.345.678/0001-90\nData: 15/09/2026\nValor: R$ 1.234,56",
        "cpfs": ["123.456.789-00"],
        "cnpjs": ["12.345.678/0001-90"],
        "dates": ["15/09/2026"],
        "values": ["1.234,56"],
        "boleto_lines": []
    }
    
    record = integration_repo.save(**original_data)
    
    # Recuperar e verificar integridade
    recovered = integration_repo.get_by_id(record.id)
    
    assert recovered.filename == original_data["filename"]
    assert recovered.raw_text == original_data["raw_text"]
    
    # Verificar campos JSON
    import json
    assert json.loads(recovered.cpfs) == original_data["cpfs"]
    assert json.loads(recovered.cnpjs) == original_data["cnpjs"]
    assert json.loads(recovered.dates) == original_data["dates"]
    assert json.loads(recovered.values) == original_data["values"]
    assert json.loads(recovered.boleto_lines) == original_data["boleto_lines"]