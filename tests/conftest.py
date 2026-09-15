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
from PIL import Image
import numpy as np
import cv2

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
def sample_boleto_image():
    """Cria uma imagem simulando um boleto para testes.

    Returns:
        Bytes de uma imagem PNG simulando um boleto.
    """
    img = Image.new('RGB', (400, 600), color='white')
    
    # Adicionar alguns elementos para simular um boleto
    from PIL import ImageDraw, ImageFont
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
