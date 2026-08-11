import pytest
import numpy as np
import cv2
from smart_ocr_finance.preprocessing.processor import ImageProcessor


@pytest.fixture
def dummy_color_image():
    """Cria uma imagem de teste 100x100 colorida."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = (255, 0, 0)  # Azul
    return img

@pytest.fixture
def dummy_document_image():
    """Cria uma imagem forjada com um retângulo branco em um fundo preto (simulando um documento)"""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Desenha um retângulo branco simulando a folha
    cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
    return img

def test_to_grayscale(dummy_color_image):
    gray = ImageProcessor.to_grayscale(dummy_color_image)
    assert len(gray.shape) == 2
    assert gray.shape == (100, 100)

def test_to_grayscale_already_gray():
    gray = np.zeros((100, 100), dtype=np.uint8)
    out = ImageProcessor.to_grayscale(gray)
    assert len(out.shape) == 2

def test_apply_blur(dummy_color_image):
    blurred = ImageProcessor.apply_blur(dummy_color_image, ksize=(3, 3))
    assert blurred.shape == dummy_color_image.shape

def test_apply_threshold(dummy_color_image):
    thresh = ImageProcessor.apply_threshold(dummy_color_image)
    assert len(thresh.shape) == 2
    # Valores do threshold binário devem ser 0 ou 255
    unique_vals = np.unique(thresh)
    assert set(unique_vals).issubset({0, 255})

def test_get_document_contours(dummy_document_image):
    pts = ImageProcessor.get_document_contours(dummy_document_image)
    assert pts is not None
    assert len(pts) == 4

def test_fix_perspective(dummy_document_image):
    warped = ImageProcessor.fix_perspective(dummy_document_image)
    assert warped is not None
    # Deve cortar exatamente a parte branca
    assert warped.shape[0] > 0
    assert warped.shape[1] > 0

def test_fix_perspective_no_document():
    # Uma imagem sem contorno claro
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    warped = ImageProcessor.fix_perspective(blank)
    # Se não encontra, devolve a original
    assert np.array_equal(warped, blank)
