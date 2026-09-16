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
def dummy_grayscale_image():
    """Cria uma imagem de teste 100x100 em escala de cinza."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[:, :] = 128
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

def test_to_grayscale_already_gray(dummy_grayscale_image):
    """Testa que já escala de cinza permanece inalterada."""
    out = ImageProcessor.to_grayscale(dummy_grayscale_image)
    assert len(out.shape) == 2
    assert np.array_equal(out, dummy_grayscale_image)

def test_to_grayscale_rgba():
    """Testa conversão de RGBA para grayscale."""
    rgba = np.zeros((100, 100, 4), dtype=np.uint8)
    rgba[:, :] = (255, 0, 0, 255)
    gray = ImageProcessor.to_grayscale(rgba)
    assert len(gray.shape) == 2
    assert gray.shape == (100, 100)

def test_apply_blur(dummy_color_image):
    blurred = ImageProcessor.apply_blur(dummy_color_image, ksize=(3, 3))
    assert blurred.shape == dummy_color_image.shape

def test_apply_blur_different_ksize(dummy_color_image):
    """Testa blur com diferentes tamanhos de kernel."""
    blurred_5x5 = ImageProcessor.apply_blur(dummy_color_image, ksize=(5, 5))
    blurred_7x7 = ImageProcessor.apply_blur(dummy_color_image, ksize=(7, 7))
    
    assert blurred_5x5.shape == dummy_color_image.shape
    assert blurred_7x7.shape == dummy_color_image.shape
    # Imagens diferentes devem ter valores diferentes devido ao blur
    assert not np.array_equal(blurred_5x5, blurred_7x7)

def test_apply_threshold(dummy_color_image):
    thresh = ImageProcessor.apply_threshold(dummy_color_image)
    assert len(thresh.shape) == 2
    # Valores do threshold binário devem ser 0 ou 255
    unique_vals = np.unique(thresh)
    assert set(unique_vals).issubset({0, 255})

def test_apply_threshold_grayscale(dummy_grayscale_image):
    """Testa threshold em imagem já grayscale."""
    thresh = ImageProcessor.apply_threshold(dummy_grayscale_image)
    assert len(thresh.shape) == 2
    unique_vals = np.unique(thresh)
    assert set(unique_vals).issubset({0, 255})

def test_apply_threshold_custom_params(dummy_color_image):
    """Testa threshold com parâmetros customizados."""
    thresh = ImageProcessor.apply_threshold(dummy_color_image, block_size=15, C=3)
    assert len(thresh.shape) == 2
    unique_vals = np.unique(thresh)
    assert set(unique_vals).issubset({0, 255})

def test_get_document_contours(dummy_document_image):
    pts = ImageProcessor.get_document_contours(dummy_document_image)
    assert pts is not None
    assert len(pts) == 4

def test_get_document_contours_no_document():
    """Testa detecção de contorno em imagem sem documento."""
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    pts = ImageProcessor.get_document_contours(blank)
    assert pts is None

def test_get_document_contours_complex_document():
    """Testa detecção em documento mais complexo."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    # Documento maior com bordas mais definidas
    cv2.rectangle(img, (30, 30), (270, 270), (255, 255, 255), -1)
    cv2.rectangle(img, (30, 30), (270, 270), (0, 0, 0), 3)  # Borda preta
    
    pts = ImageProcessor.get_document_contours(img)
    assert pts is not None
    assert len(pts) == 4

def test_order_points():
    """Testa ordenação de pontos."""
    pts = np.array([[10, 10], [100, 10], [100, 100], [10, 100]], dtype=np.float32)
    ordered = ImageProcessor.order_points(pts)
    
    # Deve retornar 4 pontos ordenados
    assert ordered.shape == (4, 2)
    # Top-left deve ter menor soma
    assert ordered[0].sum() == pts[0].sum()
    # Bottom-right deve ter maior soma
    assert ordered[2].sum() == pts[2].sum()

def test_four_point_transform(dummy_document_image):
    """Testa transformação de perspectiva."""
    pts = np.array([[50, 50], [150, 50], [150, 150], [50, 150]], dtype=np.float32)
    warped = ImageProcessor.four_point_transform(dummy_document_image, pts)
    
    assert warped is not None
    assert warped.shape[0] > 0
    assert warped.shape[1] > 0
    # Imagem transformada deve ter formato diferente
    assert warped.shape != dummy_document_image.shape

def test_fix_perspective(dummy_document_image):
    warped = ImageProcessor.fix_perspective(dummy_document_image)
    assert warped is not None
    # Deve cortar exatamente a parte branca
    assert warped.shape[0] > 0
    assert warped.shape[1] > 0

def test_fix_perspective_no_document():
    """Testa fix_perspective quando não encontra documento."""
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    warped = ImageProcessor.fix_perspective(blank)
    # Se não encontra, devolve a original
    assert np.array_equal(warped, blank)

def test_fix_perspective_partial_document():
    """Testa fix_perspective com documento parcial."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Documento parcial (apenas metade)
    cv2.rectangle(img, (50, 50), (150, 100), (255, 255, 255), -1)
    
    warped = ImageProcessor.fix_perspective(img)
    # Deve retornar algo (pode ser a original ou transformada)
    assert warped is not None
    assert warped.shape == img.shape
