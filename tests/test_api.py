import pytest
from fastapi.testclient import TestClient
from app.main import app
from smart_ocr_finance.services.ocr_service import OCRService
import numpy as np
import cv2

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "project" in response.json()
    assert response.json()["status"] == "online"

@pytest.fixture
def dummy_image_bytes():
    """Gera um arquivo de imagem em memória (bytes) para upload."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", img)
    return encoded.tobytes()

def test_extract_endpoint_no_file():
    # Enviar sem arquivo deve retornar 422 Unprocessable Entity do FastAPI
    response = client.post("/api/v1/extract")
    assert response.status_code == 422

def test_extract_endpoint_invalid_mime():
    # Enviar um TXT fingindo ser imagem (erro 400 da nossa rota)
    files = {"file": ("test.txt", b"Texto qualquer", "text/plain")}
    response = client.post("/api/v1/extract", files=files)
    assert response.status_code == 400
    assert "imagem" in response.json()["detail"].lower()

def test_extract_endpoint_success(dummy_image_bytes, monkeypatch):
    # Faz o mock do serviço OCR para não instanciar o EasyOCR (peso na rede/memória)
    class MockOCRService:
        def process_image(self, img_bytes):
            return {
                "cpfs": ["111.111.111-11"],
                "cnpjs": [],
                "dates": ["10/10/2023"],
                "values": ["1.000,00"],
                "boleto_lines": [],
                "raw_text": "Texto extraído mock"
            }
            
    # Sobrescreve a dependência na API
    app.dependency_overrides[OCRService] = MockOCRService
    
    # Executa a chamada
    files = {"file": ("test.png", dummy_image_bytes, "image/png")}
    response = client.post("/api/v1/extract", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "111.111.111-11" in data["cpfs"]
    assert "10/10/2023" in data["dates"]
    
    # Limpa override
    app.dependency_overrides.clear()
