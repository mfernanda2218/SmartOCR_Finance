"""
Wrapper do logger para uso na API.
"""

from loguru import logger
from src.config import settings
import sys
from pathlib import Path

def setup_logger():
    """Configura o logger loguru"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Remover handler padrão
    logger.remove()
    
    # Adicionar handler para console
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Adicionar handler para arquivo
    logger.add(
        log_dir / "app.log",
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )

# Configurar logger ao importar
setup_logger()

# Exportar logger como 'log' para compatibilidade
log = logger

__all__ = ["log"]