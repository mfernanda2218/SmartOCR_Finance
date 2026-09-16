"""Fixtures compartilhadas para os testes do SmartOCR Finance.

Este arquivo é automaticamente carregado pelo pytest antes de
executar qualquer teste. As fixtures aqui definidas ficam
disponíveis para todos os módulos de teste sem necessidade
de importação explícita.

Conceitos:
    - Fixture: Função que prepara (setup) e limpa (teardown) o
      ambiente necessário para um teste.
    - conftest.py: Arquivo especial do pytest para fixtures globais.
    - tmp_path: Fixture built-in do pytest que cria um diretório
      temporário único para cada teste.
"""

from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from typing import Optional

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smart_ocr_finance.utils.config import Settings
from src.models.database import Base
from src.models.extraction_record import ExtractionRecord


@pytest.fixture
def sample_settings() -> Settings:
    """Cria uma instância de Settings com valores padrão para testes.

    Returns:
        Settings configurado para ambiente de teste.
    """
    return Settings()


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Cria uma estrutura de diretórios temporária para testes.

    Simula a estrutura data/ do projeto em um diretório temporário,
    útil para testes que precisam ler/escrever arquivos sem afetar
    os dados reais do projeto.

    Args:
        tmp_path: Fixture built-in do pytest — diretório temporário único.

    Returns:
        Path para o diretório temporário com a estrutura data/ criada.
    """
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    samples = tmp_path / "samples"

    raw.mkdir()
    processed.mkdir()
    samples.mkdir()

    return tmp_path


@pytest.fixture
def sample_image_bytes():
    """Cria uma imagem de teste em bytes.

    Returns:
        Bytes de uma imagem PNG de teste (100x100 pixels).
    """
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_image_bytes_custom(size: tuple = (100, 100), color: str = 'red'):
    """Cria uma imagem de teste customizada em bytes.

    Args:
        size: Tupla (width, height) da imagem.
        color: Cor da imagem em formato RGB ou nome de cor.

    Returns:
        Bytes de uma imagem PNG de teste customizada.
    """
    img = Image.new('RGB', size, color=color)
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_boleto_image():
    """Cria uma imagem simulando um boleto para testes.

    Returns:
        Bytes de uma imagem PNG simulando um boleto.
    """
    img = Image.new('RGB', (400, 600), color='white')
    
    # Adicionar alguns elementos para simular um boleto
    draw = ImageDraw.Draw(img)
    
    # Linhas do boleto
    draw.rectangle([50, 50, 350, 100], outline='black', width=2)
    draw.rectangle([50, 120, 350, 200], outline='black', width=2)
    draw.rectangle([50, 220, 350, 280], outline='black', width=2)
    
    # Texto simulado
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((60, 60), "BANCO XXX", fill='black', font=font)
    draw.text((60, 130), "CPF: 123.456.789-00", fill='black', font=font)
    draw.text((60, 150), "Vencimento: 15/09/2026", fill='black', font=font)
    draw.text((60, 170), "Valor: R$ 1.250,00", fill='black', font=font)
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_document_image():
    """Cria uma imagem simulando um documento genérico.

    Returns:
        Bytes de uma imagem PNG simulando um documento.
    """
    img = Image.new('RGB', (300, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Borda do documento
    draw.rectangle([10, 10, 290, 390], outline='black', width=2)
    
    # Linhas de texto simuladas
    for i in range(10):
        y = 50 + i * 30
        draw.rectangle([30, y, 270, y + 15], fill='gray')
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def numpy_image_color():
    """Cria uma imagem numpy colorida para testes.

    Returns:
        Array numpy (100x100x3) BGR.
    """
    return np.zeros((100, 100, 3), dtype=np.uint8)


@pytest.fixture
def numpy_image_grayscale():
    """Cria uma imagem numpy em escala de cinza para testes.

    Returns:
        Array numpy (100x100) grayscale.
    """
    return np.zeros((100, 100), dtype=np.uint8)


@pytest.fixture(scope="function")
def db_session():
    """Cria um banco de dados em memória isolado para cada teste.

    Returns:
        Session do SQLAlchemy com banco em memória.
    """
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
def clean_database(db_session):
    """Limpa o banco de dados antes e depois do teste.

    Args:
        db_session: Session do SQLAlchemy.

    Yields:
        Session limpa para uso no teste.
    """
    db_session.query(ExtractionRecord).delete()
    db_session.commit()
    yield db_session
    db_session.query(ExtractionRecord).delete()
    db_session.commit()


@pytest.fixture
def mock_ocr_result():
    """Retorna um resultado mockado do OCR para testes.

    Returns:
        Dicionário com estrutura padrão de resultado OCR.
    """
    return {
        "cpfs": ["123.456.789-00"],
        "cnpjs": [],
        "dates": ["15/09/2026"],
        "values": ["1.250,00"],
        "boleto_lines": [],
        "raw_text": "CPF: 123.456.789-00\nVencimento: 15/09/2026\nValor: R$ 1.250,00",
        "metadata": {
            "document_type": "boleto",
            "processing_status": "success",
            "confidence_score": 0.95,
            "processing_time_ms": 1500,
            "warnings": []
        }
    }


@pytest.fixture
def sample_text_data():
    """Retorna texto de exemplo com dados financeiros.

    Returns:
        String com texto contendo CPF, CNPJ, datas e valores.
    """
    return """
    CONTA DE ENERGIA
    =================
    Cliente: João Silva
    CPF: 123.456.789-00
    CNPJ: 12.345.678/0001-90 (se aplicável)
    
    Referência: Setembro/2026
    Vencimento: 15/09/2026
    Valor a pagar: R$ 250,50
    
    Linha digitável: 34191.09008 63396.873738 09516.480008 8 91320000015000
    """


@pytest.fixture
def various_cpf_samples():
    """Retorna uma lista de CPFs para testes.

    Returns:
        Lista de CPFs em diferentes formatos.
    """
    return [
        "52998224725",           # Sem formatação
        "529.982.247-25",        # Com formatação
        "111.111.111-11",        # Inválido (todos iguais)
        "123.456.789-00",        # Inválido
    ]


@pytest.fixture
def various_cnpj_samples():
    """Retorna uma lista de CNPJs para testes.

    Returns:
        Lista de CNPJs em diferentes formatos.
    """
    return [
        "11444777000161",        # Sem formatação
        "11.444.777/0001-61",    # Com formatação
        "11.111.111/1111-11",    # Inválido (todos iguais)
        "12.345.678/0001-99",    # Inválido
    ]


@pytest.fixture
def various_date_samples():
    """Retorna uma lista de datas em diferentes formatos.

    Returns:
        Lista de datas em diferentes formatos.
    """
    return [
        "15/09/2026",            # Formato brasileiro
        "15-09-2026",            # Com hífens
        "2026/09/15",            # Formato ISO
        "15.09.2026",            # Com pontos
        "September 15, 2026",    # Inglês
    ]


@pytest.fixture
def various_value_samples():
    """Retorna uma lista de valores monetários em diferentes formatos.

    Returns:
        Lista de valores em diferentes formatos.
    """
    return [
        "R$ 1.250,00",           # Com R$ e pontos
        "R$ 1250,00",            # Com R$ sem pontos
        "1.250,00",              # Sem R$ com pontos
        "1250,00",               # Sem R$ sem pontos
        "R$ 1250",               # Sem centavos
    ]


# Configuração para pular testes que requerem dependências externas
def pytest_configure(config):
    """Configura hooks personalizados do pytest."""
    config.addinivalue_line(
        "markers", "slow: marca testes que são lentos e podem ser skipados"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "requires_postgres: marca testes que requerem PostgreSQL"
    )
