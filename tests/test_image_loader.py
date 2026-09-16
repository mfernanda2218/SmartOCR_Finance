import pytest
import numpy as np
import cv2
from pathlib import Path
from smart_ocr_finance.preprocessing.image_loader import ImageLoader

@pytest.fixture
def dummy_image_path(tmp_path):
    """Cria uma imagem de teste temporária."""
    img_path = tmp_path / "test_image.png"
    # Cria uma imagem 100x100 preta
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)
    return img_path

@pytest.fixture
def invalid_image_path(tmp_path):
    """Cria um arquivo que não é uma imagem válida."""
    txt_path = tmp_path / "not_an_image.txt"
    txt_path.write_text("dummy text content")
    return txt_path

def test_load_image_success(dummy_image_path):
    img = ImageLoader.load_image(dummy_image_path)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 100, 3)

def test_load_image_file_not_found():
    img = ImageLoader.load_image(Path("caminho_inexistente_999.png"))
    assert img is None

def test_load_image_invalid_file(invalid_image_path):
    img = ImageLoader.load_image(invalid_image_path)
    assert img is None

def test_load_image_from_bytes(dummy_image_path):
    # Lê os bytes brutos do arquivo gerado
    with open(dummy_image_path, "rb") as f:
        img_bytes = f.read()
    
    img = ImageLoader.load_image_from_bytes(img_bytes)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 100, 3)

def test_load_image_from_bytes_invalid():
    img = ImageLoader.load_image_from_bytes(b"invalid data")
    assert img is None

def test_load_image_from_bytes_empty():
    img = ImageLoader.load_image_from_bytes(b"")
    assert img is None

def test_save_image(tmp_path):
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    save_path = tmp_path / "saved_img.png"
    
    success = ImageLoader.save_image(img, save_path)
    assert success is True
    assert save_path.exists()

def test_save_image_creates_directory(tmp_path):
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    save_path = tmp_path / "subdir" / "nested" / "saved_img.png"
    
    success = ImageLoader.save_image(img, save_path)
    assert success is True
    assert save_path.exists()

def test_save_image_invalid_array(tmp_path):
    img = "not an image"
    save_path = tmp_path / "invalid.png"
    
    success = ImageLoader.save_image(img, save_path)
    assert success is False

def test_validate_image_valid():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    assert ImageLoader.validate_image(img) is True

def test_validate_image_grayscale():
    img = np.zeros((10, 10), dtype=np.uint8)
    assert ImageLoader.validate_image(img) is True

def test_validate_image_empty():
    img = np.array([])
    assert ImageLoader.validate_image(img) is False

def test_validate_image_not_numpy():
    img = [[0, 0], [0, 0]]
    assert ImageLoader.validate_image(img) is False

def test_validate_image_1d():
    img = np.array([1, 2, 3, 4])
    assert ImageLoader.validate_image(img) is False

def test_validate_image_different_formats():
    # Teste RGB
    img_rgb = np.zeros((10, 10, 3), dtype=np.uint8)
    assert ImageLoader.validate_image(img_rgb) is True
    
    # Teste RGBA
    img_rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    assert ImageLoader.validate_image(img_rgba) is True
    
    # Teste grayscale
    img_gray = np.zeros((10, 10), dtype=np.uint8)
    assert ImageLoader.validate_image(img_gray) is True
