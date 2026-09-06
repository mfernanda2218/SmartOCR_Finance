"""
Módulo de configuração para a API FastAPI.
Configurações centralizadas usando pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=False)

class Settings(BaseSettings):
    """
    Configurações principais da aplicação.
    Lidas automaticamente a partir do arquivo .env ou variáveis de ambiente.
    """
    # Geral
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "SmartOCR Finance API"
    VERSION: str = "0.1.0"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Banco de Dados
    DATABASE_URL: str = "sqlite:///./smartocr.db"

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: str = "logs"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"

    # OCR
    OCR_ENGINE: str = "easyocr"
    OCR_LANGUAGE: str = "por"

    # Diretórios
    DATA_DIR: str = "data"
    MODELS_DIR: str = "models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Instância global
settings = Settings()