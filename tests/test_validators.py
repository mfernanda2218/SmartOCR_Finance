import pytest
from smart_ocr_finance.validation.validators import DocumentValidator

def test_validate_cpf_valid():
    # CPFs gerados aleatoriamente válidos matematicamente (não reais)
    assert DocumentValidator.validate_cpf("52998224725") is True
    assert DocumentValidator.validate_cpf("529.982.247-25") is True

def test_validate_cpf_invalid():
    assert DocumentValidator.validate_cpf("111.111.111-11") is False
    assert DocumentValidator.validate_cpf("123.456.789-00") is False

def test_validate_cnpj_valid():
    # CNPJ gerado aleatoriamente válido matematicamente
    assert DocumentValidator.validate_cnpj("11.444.777/0001-61") is True
    assert DocumentValidator.validate_cnpj("11444777000161") is True

def test_validate_cnpj_invalid():
    assert DocumentValidator.validate_cnpj("11.111.111/1111-11") is False
    assert DocumentValidator.validate_cnpj("12.345.678/0001-99") is False
