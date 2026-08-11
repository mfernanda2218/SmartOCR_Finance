"""Módulo de configuração do SmartOCR Finance.

Responsável por centralizar todas as configurações do projeto,
carregando valores de variáveis de ambiente com fallback para
padrões sensatos.

Conceitos aplicados:
    - 12-Factor App: Configuração separada do código
    - python-dotenv: Carregamento de arquivos .env
    - dataclass: Estruturação tipo-segura de configurações
    - Path (pathlib): Manipulação de caminhos multiplataforma
"""

from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

import os

# Carrega variáveis do arquivo .env (se existir) para os.environ.
# override=False garante que variáveis já definidas no sistema
# não serão sobrescritas — comportamento esperado em produção.
load_dotenv(override=False)


# =============================================================================
# Diretórios do Projeto
# =============================================================================

# BASE_DIR aponta para a raiz do projeto (2 níveis acima deste arquivo)
# src/utils/config.py -> src/utils -> src -> raiz
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# Diretórios principais — podem ser sobrescritos via variáveis de ambiente
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
SAMPLES_DIR: Path = DATA_DIR / "samples"
MODELS_DIR: Path = Path(os.getenv("MODELS_DIR", str(BASE_DIR / "models")))
LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(BASE_DIR / "logs")))


@dataclass(frozen=True)
class Settings:
    """Configurações centralizadas do SmartOCR Finance.

    Utiliza um dataclass imutável (frozen=True) para garantir que
    as configurações não sejam alteradas acidentalmente após a
    inicialização.

    Attributes:
        environment: Ambiente de execução (development/staging/production).
        log_level: Nível mínimo de log a ser registrado.
        log_rotation: Tamanho máximo do arquivo de log antes de rotacionar.
        log_retention: Tempo de retenção dos arquivos de log.
        ocr_engine: Engine de OCR padrão (tesseract/easyocr).
        ocr_language: Idioma padrão para OCR.
        base_dir: Diretório raiz do projeto.
        data_dir: Diretório de dados.
        models_dir: Diretório de modelos treinados.
        log_dir: Diretório de logs.
    """

    # Geral
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )

    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "DEBUG")
    )
    log_rotation: str = field(
        default_factory=lambda: os.getenv("LOG_ROTATION", "10 MB")
    )
    log_retention: str = field(
        default_factory=lambda: os.getenv("LOG_RETENTION", "7 days")
    )

    # OCR
    ocr_engine: str = field(
        default_factory=lambda: os.getenv("OCR_ENGINE", "tesseract")
    )
    ocr_language: str = field(
        default_factory=lambda: os.getenv("OCR_LANGUAGE", "por")
    )

    # Caminhos (derivados das constantes de módulo)
    base_dir: Path = field(default=BASE_DIR)
    data_dir: Path = field(default_factory=lambda: DATA_DIR)
    models_dir: Path = field(default_factory=lambda: MODELS_DIR)
    log_dir: Path = field(default_factory=lambda: LOG_DIR)

    def __post_init__(self) -> None:
        """Validações executadas após a inicialização."""
        valid_environments = {"development", "staging", "production"}
        if self.environment not in valid_environments:
            raise ValueError(
                f"Ambiente inválido: '{self.environment}'. "
                f"Valores válidos: {valid_environments}"
            )

        valid_engines = {"tesseract", "easyocr"}
        if self.ocr_engine not in valid_engines:
            raise ValueError(
                f"Engine OCR inválida: '{self.ocr_engine}'. "
                f"Valores válidos: {valid_engines}"
            )

    def __repr__(self) -> str:
        """Representação legível das configurações."""
        return (
            f"Settings(\n"
            f"  environment={self.environment!r},\n"
            f"  log_level={self.log_level!r},\n"
            f"  ocr_engine={self.ocr_engine!r},\n"
            f"  ocr_language={self.ocr_language!r},\n"
            f"  base_dir={self.base_dir!s},\n"
            f"  data_dir={self.data_dir!s},\n"
            f"  models_dir={self.models_dir!s},\n"
            f"  log_dir={self.log_dir!s}\n"
            f")"
        )


# Instância global de configurações — importável diretamente:
# from src.utils.config import settings
settings = Settings()
