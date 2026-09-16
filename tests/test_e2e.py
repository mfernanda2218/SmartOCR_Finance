"""Testes End-to-End (E2E) para o SmartOCR Finance.

Estes testes validam o fluxo completo da aplicação, desde o upload
de imagem até a persistência no banco de dados e recuperação via API.
"""

import pytest
import httpx
from httpx import AsyncClient
from app.main import app
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.models.extraction_record import ExtractionRecord
from src.repositories.extraction_repository import ExtractionRepository
from src.api.routes import get_db


@pytest.fixture(scope="function")
def test_db():
    """Cria banco de dados em memória para testes E2E."""
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def mock_ocr_service():
    """Mock do serviço OCR para evitar dependência de EasyOCR nos testes."""
    with patch("smart_ocr_finance.services.ocr_service.OCREngine") as mock_engine:
        mock_instance = MagicMock()
        mock_engine.return_value = mock_instance
        mock_instance.extract_text.return_value = [
            "CPF: 123.456.789-00",
            "Vencimento: 15/09/2026",
            "Valor: R$ 1.250,00",
            "CNPJ: 12.345.678/0001-90"
        ]
        mock_instance.get_full_text.return_value = "CPF: 123.456.789-00\nVencimento: 15/09/2026\nValor: R$ 1.250,00\nCNPJ: 12.345.678/0001-90"
        yield mock_instance


@pytest.mark.asyncio
async def test_full_extraction_flow(sample_boleto_image, mock_ocr_service, test_db):
    """Testa o fluxo completo de extração: upload -> processamento -> persistência -> recuperação."""
    
    # Configurar mock para o repositório
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
            # 1. Upload de imagem
            response = await client.post(
                "/api/v1/extract",
                files={"file": ("boleto.png", sample_boleto_image, "image/png")}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 2. Validar estrutura da resposta
            assert "cpfs" in data
            assert "cnpjs" in data
            assert "dates" in data
            assert "values" in data
            assert "boleto_lines" in data
            assert "raw_text" in data
            assert "metadata" in data
            
            # 3. Validar dados extraídos
            assert len(data["cpfs"]) > 0
            assert len(data["cnpjs"]) > 0
            assert len(data["dates"]) > 0
            assert len(data["values"]) > 0
            assert data["raw_text"] is not None
            
            # 4. Validar metadados
            assert "document_type" in data["metadata"]
            assert "processing_status" in data["metadata"]
            assert "confidence_score" in data["metadata"]
            assert "processing_time_ms" in data["metadata"]
            
            # 5. Validar que dados foram persistidos no banco
            repo = ExtractionRepository(test_db)
            records = repo.get_all()
            assert len(records) > 0
            
            # 6. Validar que podemos recuperar o registro via API
            record_id = records[0].id
            history_response = await client.get("/api/v1/history")
            assert history_response.status_code == 200
            history_data = history_response.json()
            assert len(history_data["records"]) > 0
            
            # 7. Validar que podemos buscar registro específico
            record_response = await client.get(f"/api/v1/history/{record_id}")
            assert record_response.status_code == 200
            record_data = record_response.json()
            assert record_data["id"] == record_id
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_extract_endpoint_validation(sample_image_bytes):
    """Testa validação de entrada no endpoint de extração."""
    
    async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
        # Testar sem arquivo
        response = await client.post("/api/v1/extract")
        assert response.status_code == 422
        
        # Testar com arquivo inválido (texto)
        response = await client.post(
            "/api/v1/extract",
            files={"file": ("test.txt", b"texto", "text/plain")}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_history_endpoint_pagination(test_db):
    """Testa paginação do endpoint de histórico."""
    
    # Criar alguns registros de teste
    repo = ExtractionRepository(test_db)
    for i in range(5):
        repo.save(
            filename=f"test{i}.png",
            raw_text=f"Texto de teste {i}",
            cpfs=[f"123.456.789-0{i}"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=[f"{(i+1)*100}.00"],
            boleto_lines=[]
        )
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
            # Testar paginação
            response = await client.get("/api/v1/history?skip=0&limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["records"]) == 2
            
            response = await client.get("/api/v1/history?skip=2&limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["records"]) == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_record_flow(test_db):
    """Testa o fluxo de deleção de um registro."""
    
    # Criar registro de teste
    repo = ExtractionRepository(test_db)
    record = repo.save(
        filename="delete_test.png",
        raw_text="Texto para deletar",
        cpfs=["123.456.789-00"],
        cnpjs=[],
        dates=["15/09/2026"],
        values=["100.00"],
        boleto_lines=[]
    )
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
            # Deletar registro
            response = await client.delete(f"/api/v1/history/{record.id}")
            assert response.status_code == 200
            
            # Verificar que foi deletado
            response = await client.get(f"/api/v1/history/{record.id}")
            assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_stats_endpoint(test_db):
    """Testa o endpoint de estatísticas."""
    
    # Criar registros de teste com diferentes características
    repo = ExtractionRepository(test_db)
    repo.save("a.png", "txt", ["123.456.789-00"], [], ["15/09/2026"], ["100.00"], [])
    repo.save("b.png", "txt", [], ["12.345.678/0001-90"], ["20/09/2026"], ["200.00"], [])
    repo.save("c.png", "txt", ["987.654.321-00"], [], ["25/09/2026"], ["300.00"], [])
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
            response = await client.get("/api/v1/stats")
            assert response.status_code == 200
            data = response.json()
            
            # Validar estrutura
            assert "total_extractions" in data
            assert "documents_with_cpf" in data
            assert "documents_with_cnpj" in data
            assert "documents_with_values" in data
            assert "average_fields_per_document" in data
            assert "successful_extractions" in data
            
            # Validar valores
            assert data["total_extractions"] == 3
            assert data["documents_with_cpf"] == 2
            assert data["documents_with_cnpj"] == 1
            assert data["documents_with_values"] == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check():
    """Testa o endpoint de health check."""
    
    async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"