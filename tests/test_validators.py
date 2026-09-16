import pytest
from smart_ocr_finance.validation.validators import DocumentValidator

def test_validate_cpf_valid():
    # CPFs gerados aleatoriamente válidos matematicamente (não reais)
    assert DocumentValidator.validate_cpf("52998224725") is True
    assert DocumentValidator.validate_cpf("529.982.247-25") is True

def test_validate_cpf_invalid():
    assert DocumentValidator.validate_cpf("111.111.111-11") is False
    assert DocumentValidator.validate_cpf("123.456.789-00") is False

def test_validate_cpf_empty():
    """Testa validação de CPF vazio."""
    assert DocumentValidator.validate_cpf("") is False
    assert DocumentValidator.validate_cpf(None) is False

def test_validate_cpf_wrong_length():
    """Testa CPF com comprimento incorreto."""
    assert DocumentValidator.validate_cpf("123") is False
    assert DocumentValidator.validate_cpf("123456789012345") is False

def test_validate_cpf_with_letters():
    """Testa CPF com letras."""
    assert DocumentValidator.validate_cpf("123.456.789-AB") is False

def test_validate_cnpj_valid():
    # CNPJ gerado aleatoriamente válido matematicamente
    assert DocumentValidator.validate_cnpj("11.444.777/0001-61") is True
    assert DocumentValidator.validate_cnpj("11444777000161") is True

def test_validate_cnpj_invalid():
    assert DocumentValidator.validate_cnpj("11.111.111/1111-11") is False
    assert DocumentValidator.validate_cnpj("12.345.678/0001-99") is False

def test_validate_cnpj_empty():
    """Testa validação de CNPJ vazio."""
    assert DocumentValidator.validate_cnpj("") is False
    assert DocumentValidator.validate_cnpj(None) is False

def test_validate_cnpj_wrong_length():
    """Testa CNPJ com comprimento incorreto."""
    assert DocumentValidator.validate_cnpj("123") is False
    assert DocumentValidator.validate_cnpj("12345678901234567890") is False

def test_validate_cnpj_with_letters():
    """Testa CNPJ com letras."""
    assert DocumentValidator.validate_cnpj("12.345.678/0001-AB") is False

# Testes parametrizados para CPF
@pytest.mark.parametrize("cpf,expected", [
    ("52998224725", True),      # Válido sem formatação
    ("529.982.247-25", True),   # Válido com formatação
    ("111.111.111-11", False),  # Inválido (todos iguais)
    ("123.456.789-00", False),  # Inválido
    ("", False),                # Vazio
    ("123", False),             # Curto
    ("123456789012345", False),  # Longo
    ("ABC.DEF.GHI-JK", False),  # Com letras
])
def test_validate_cpf_parametrized(cpf, expected):
    """Testa validação de CPF com diferentes formatos."""
    result = DocumentValidator.validate_cpf(cpf)
    assert result == expected

# Testes parametrizados para CNPJ
@pytest.mark.parametrize("cnpj,expected", [
    ("11.444.777/0001-61", True),   # Válido com formatação
    ("11444777000161", True),       # Válido sem formatação
    ("11.111.111/1111-11", False),  # Inválido (todos iguais)
    ("12.345.678/0001-99", False),  # Inválido
    ("", False),                    # Vazio
    ("123", False),                 # Curto
    ("12345678901234567890", False), # Longo
    ("12.345.678/0001-AB", False),  # Com letras
])
def test_validate_cnpj_parametrized(cnpj, expected):
    """Testa validação de CNPJ com diferentes formatos."""
    result = DocumentValidator.validate_cnpj(cnpj)
    assert result == expected
