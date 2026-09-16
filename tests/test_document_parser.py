import pytest
from smart_ocr_finance.parser.document_parser import DocumentParser

def test_extract_cpfs():
    text = "O cliente portador do CPF 123.456.789-00 realizou a compra."
    cpfs = DocumentParser.extract_cpfs(text)
    assert cpfs == ["123.456.789-00"]

def test_extract_cpfs_multiple():
    """Testa extração de múltiplos CPFs."""
    text = "CPF 123.456.789-00 e CPF 987.654.321-00 participantes."
    cpfs = DocumentParser.extract_cpfs(text)
    assert len(cpfs) == 2
    assert "123.456.789-00" in cpfs
    assert "987.654.321-00" in cpfs

def test_extract_cpfs_no_cpf():
    """Testa texto sem CPF."""
    text = "Este texto não contém nenhum CPF válido."
    cpfs = DocumentParser.extract_cpfs(text)
    assert len(cpfs) == 0

def test_extract_cpfs_invalid_format():
    """Testa CPF com formato inválido."""
    text = "CPF 123.456.789-ABC não é válido."
    cpfs = DocumentParser.extract_cpfs(text)
    assert len(cpfs) == 0

def test_extract_cnpjs():
    text = "Empresa X, CNPJ 12.345.678/0001-99 solicitou nota."
    cnpjs = DocumentParser.extract_cnpjs(text)
    assert cnpjs == ["12.345.678/0001-99"]

def test_extract_cnpjs_multiple():
    """Testa extração de múltiplos CNPJs."""
    text = "CNPJ 12.345.678/0001-99 e CNPJ 98.765.432/0001-10."
    cnpjs = DocumentParser.extract_cnpjs(text)
    assert len(cnpjs) == 2

def test_extract_cnpjs_no_cnpj():
    """Testa texto sem CNPJ."""
    text = "Este texto não contém CNPJ."
    cnpjs = DocumentParser.extract_cnpjs(text)
    assert len(cnpjs) == 0

def test_extract_dates():
    text = "Vencimento em 15/10/2023. Data de emissão 12-09-2023."
    dates = DocumentParser.extract_dates(text)
    assert "15/10/2023" in dates
    assert "12-09-2023" in dates

def test_extract_dates_multiple_formats():
    """Testa extração de datas em diferentes formatos."""
    text = "Datas: 15/10/2023, 12-09-2023, 2023/10/15, 15.10.2023"
    dates = DocumentParser.extract_dates(text)
    assert len(dates) >= 2  # Pelo menos alguns formatos devem ser reconhecidos

def test_extract_dates_no_dates():
    """Testa texto sem datas."""
    text = "Este texto não contém datas."
    dates = DocumentParser.extract_dates(text)
    assert len(dates) == 0

def test_extract_monetary_values():
    text = "Valor Total: R$ 1.250,50. Desconto: R$50,00."
    values = DocumentParser.extract_monetary_values(text)
    assert "1.250,50" in values
    assert "50,00" in values

def test_extract_monetary_values_multiple():
    """Testa extração de múltiplos valores monetários."""
    text = "Valores: R$ 1.250,50, R$ 500,00, R$ 1.000,00"
    values = DocumentParser.extract_monetary_values(text)
    assert len(values) == 3

def test_extract_monetary_values_without_rs():
    """Testa valores sem símbolo R$."""
    text = "Valores: 1.250,50 e 500,00"
    values = DocumentParser.extract_monetary_values(text)
    assert len(values) >= 1

def test_extract_monetary_values_no_values():
    """Testa texto sem valores monetários."""
    text = "Este texto não contém valores monetários."
    values = DocumentParser.extract_monetary_values(text)
    assert len(values) == 0

def test_extract_boleto_lines():
    # Linha digitável genérica
    text = "34191.09008 63396.873738 09516.480008 8 91320000015000"
    boletos = DocumentParser.extract_boleto_lines(text)
    assert len(boletos) == 1

def test_extract_boleto_lines_multiple():
    """Testa extração de múltiplas linhas digitáveis."""
    text = """
    34191.09008 63396.873738 09516.480008 8 91320000015000
    23791.09008 63396.873738 09516.480008 8 91320000015000
    """
    boletos = DocumentParser.extract_boleto_lines(text)
    assert len(boletos) == 2

def test_extract_boleto_lines_invalid():
    """Testa linha digitável inválida."""
    text = "12345 linha inválida"
    boletos = DocumentParser.extract_boleto_lines(text)
    assert len(boletos) == 0

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

def test_extract_all_empty_text():
    """Testa extração de texto vazio."""
    result = DocumentParser.extract_all("")
    assert result["cpfs"] == []
    assert result["cnpjs"] == []
    assert result["dates"] == []
    assert result["values"] == []
    assert result["boleto_lines"] == []
    assert result["raw_text"] == ""

def test_extract_all_whitespace_only():
    """Testa extração de apenas espaços em branco."""
    result = DocumentParser.extract_all("   \n\t   ")
    assert result["cpfs"] == []
    assert result["cnpjs"] == []
    assert result["dates"] == []
    assert result["values"] == []
    assert result["boleto_lines"] == []

# Testes parametrizados para casos extremos
@pytest.mark.parametrize("text,expected_count", [
    ("CPF 123.456.789-00", 1),
    ("CPF 123.456.789-00 e CPF 987.654.321-00", 2),
    ("Sem CPF aqui", 0),
    ("", 0),
    ("CPF 111.111.111-11 CPF 222.222.222-22 CPF 333.333.333-33", 3),
])
def test_extract_cpfs_parametrized(text, expected_count):
    """Testa extração de CPFs com diferentes cenários."""
    cpfs = DocumentParser.extract_cpfs(text)
    assert len(cpfs) == expected_count

@pytest.mark.parametrize("text,expected_count", [
    ("CNPJ 12.345.678/0001-90", 1),
    ("CNPJ 12.345.678/0001-90 e CNPJ 98.765.432/0001-10", 2),
    ("Sem CNPJ", 0),
    ("", 0),
])
def test_extract_cnpjs_parametrized(text, expected_count):
    """Testa extração de CNPJs com diferentes cenários."""
    cnpjs = DocumentParser.extract_cnpjs(text)
    assert len(cnpjs) == expected_count

@pytest.mark.parametrize("text,expected_values", [
    ("R$ 100,00", ["100,00"]),
    ("R$ 1.250,50 e R$ 500,00", ["1.250,50", "500,00"]),
    ("100,00", ["100,00"]),
    ("Sem valores", []),
])
def test_extract_values_parametrized(text, expected_values):
    """Testa extração de valores monetários com diferentes cenários."""
    values = DocumentParser.extract_monetary_values(text)
    if expected_values:
        for expected in expected_values:
            assert expected in values
    else:
        assert len(values) == 0
