import pytest
from smart_ocr_finance.parser.document_parser import DocumentParser

def test_extract_cpfs():
    text = "O cliente portador do CPF 123.456.789-00 realizou a compra."
    cpfs = DocumentParser.extract_cpfs(text)
    assert cpfs == ["123.456.789-00"]

def test_extract_cnpjs():
    text = "Empresa X, CNPJ 12.345.678/0001-99 solicitou nota."
    cnpjs = DocumentParser.extract_cnpjs(text)
    assert cnpjs == ["12.345.678/0001-99"]

def test_extract_dates():
    text = "Vencimento em 15/10/2023. Data de emissão 12-09-2023."
    dates = DocumentParser.extract_dates(text)
    assert "15/10/2023" in dates
    assert "12-09-2023" in dates

def test_extract_monetary_values():
    text = "Valor Total: R$ 1.250,50. Desconto: R$50,00."
    values = DocumentParser.extract_monetary_values(text)
    assert "1.250,50" in values
    assert "50,00" in values

def test_extract_boleto_lines():
    # Linha digitável genérica
    text = "34191.09008 63396.873738 09516.480008 8 91320000015000"
    boletos = DocumentParser.extract_boleto_lines(text)
    assert len(boletos) == 1

def test_extract_all():
    text = """
    CONTA DE ENERGIA
    Vencimento: 20/12/2023
    Valor: R$ 150,00
    CPF: 111.222.333-44
    34191.09008 63396.873738 09516.480008 8 91320000015000
    """
    result = DocumentParser.extract_all(text)
    assert "20/12/2023" in result["dates"]
    assert "150,00" in result["values"]
    assert "111.222.333-44" in result["cpfs"]
    assert len(result["boleto_lines"]) == 1
