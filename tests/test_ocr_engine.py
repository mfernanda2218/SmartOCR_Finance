import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from smart_ocr_finance.config.settings import settings
from smart_ocr_finance.ocr.engine import OCREngine

@pytest.fixture
def mock_easyocr():
    """Faz o mock da classe easyocr.Reader para evitar downloads de modelos de IA durante os testes unitários."""
    with patch("smart_ocr_finance.ocr.engine.easyocr.Reader") as mock_reader:
        instance = MagicMock()
        mock_reader.return_value = instance
        # Configura o retorno padrão do readtext
        instance.readtext.return_value = [
            ([[10, 10], [100, 10], [100, 30], [10, 30]], "VALOR TOTAL", 0.98),
            ([[10, 40], [100, 40], [100, 60], [10, 60]], "R$ 150,00", 0.95),
        ]
        yield mock_reader, instance

@pytest.fixture
def ocr_engine(mock_easyocr):
    """Retorna uma instância do OCREngine utilizando o mock do EasyOCR."""
    return OCREngine()

@pytest.fixture
def dummy_image():
    """Retorna uma imagem NumPy dummy (100x100 preta)."""
    return np.zeros((100, 100, 3), dtype=np.uint8)

def test_ocr_engine_initialization(mock_easyocr):
    mock_reader, _ = mock_easyocr
    settings.OCR_LANGUAGE = "por"
    OCREngine()
    # Verifica se instanciou com 'pt' e 'en' (mapeamento do 'por')
    mock_reader.assert_called_once_with(["pt", "en"])

def test_extract_text_detailed(ocr_engine, dummy_image, mock_easyocr):
    _, reader = mock_easyocr
    results = ocr_engine.extract_text(dummy_image, detail=1)
    
    # Validações
    assert len(results) == 2
    reader.readtext.assert_called_once_with(dummy_image, detail=1)
    
    # Estrutura do retorno detail=1
    bbox, text, conf = results[0]
    assert text == "VALOR TOTAL"
    assert conf == 0.98

def test_extract_text_simple(ocr_engine, dummy_image, mock_easyocr):
    _, reader = mock_easyocr
    # Ajustando o mock para retornar apenas as strings (quando detail=0)
    reader.readtext.return_value = ["VALOR TOTAL", "R$ 150,00"]
    
    results = ocr_engine.extract_text(dummy_image, detail=0)
    
    assert len(results) == 2
    reader.readtext.assert_called_with(dummy_image, detail=0)
    assert results[0] == "VALOR TOTAL"

def test_extract_text_empty_image(ocr_engine):
    # Passar None ou array vazio não deve chamar a engine e deve retornar lista vazia
    assert ocr_engine.extract_text(None) == []
    assert ocr_engine.extract_text(np.array([])) == []

def test_get_full_text(ocr_engine, dummy_image, mock_easyocr):
    _, reader = mock_easyocr
    reader.readtext.return_value = ["VALOR TOTAL", "R$ 150,00"]
    
    full_text = ocr_engine.get_full_text(dummy_image, separator="\n")
    assert full_text == "VALOR TOTAL\nR$ 150,00"
