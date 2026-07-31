import sys
from pathlib import Path
from loguru import logger
from config import settings

def setup_logger():
    """
    Configura o logger utilizando o loguru.
    Define a saída no console e a rotação/retenção de arquivos de log.
    """
    # Remove a configuração padrão do loguru
    logger.remove()

    # Formato padrão
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Handler para o Console
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Diretório de logs
    log_path = Path(settings.LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)

    # Handler para o Arquivo
    logger.add(
        str(log_path / "app.log"),
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
    )

    logger.debug("Logger configurado com sucesso.")
    return logger

# Instância global do logger configurado
log = setup_logger()
