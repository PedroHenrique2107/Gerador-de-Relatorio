"""
Camada de logging centralizada.

Fornece logging estruturado com suporte a múltiplos handlers.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from config.settings import LoggerConfig


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Formata log com cores."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            )
        return super().format(record)


def setup_logger(
    name: str,
    config: Optional[LoggerConfig] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Configura logger com handlers de console e arquivo.
    
    Args:
        name: Nome do logger (__name__)
        config: Configuração do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Logger configurado
    
    Exemplo:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Olá")
    """
    from config.settings import config as app_config
    
    if config is None:
        config = app_config().logger
    
    if level is None:
        level = config.level
    
    # Cria logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove handlers existentes para evitar duplicatas
    logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(config.format)
    
    # Handler: Console (colorido)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(ColoredFormatter(config.format))
    logger.addHandler(console_handler)
    
    # Handler: Arquivo
    log_file = config.log_dir / f"{name.split('.')[0]}.log"
    config.log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna logger existente ou cria novo.
    
    Args:
        name: Nome do logger (__name__)
    
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)
