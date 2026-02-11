"""
Init do módulo core.

Exporta componentes principais.
"""

from app.core.logger import setup_logger, get_logger
from app.core.database import DatabaseManager, get_engine
from app.core.venv_validator import require_venv, is_inside_venv, print_venv_status
from app.core.exceptions import (
    JSONMySQLException,
    ConfigurationError,
    DatabaseError,
    ValidationError,
    LoaderError,
    ParsingError,
    NormalizationError,
)

__all__ = [
    'setup_logger',
    'get_logger',
    'DatabaseManager',
    'get_engine',
    'require_venv',
    'is_inside_venv',
    'print_venv_status',
    'JSONMySQLException',
    'ConfigurationError',
    'DatabaseError',
    'ValidationError',
    'LoaderError',
    'ParsingError',
    'NormalizationError',
]
