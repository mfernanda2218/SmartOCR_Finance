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

import pytest

from src.utils.config import Settings


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
