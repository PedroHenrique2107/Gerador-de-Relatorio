"""
Init do módulo app.
"""

from app.core import (
    setup_logger,
    get_logger,
    DatabaseManager,
    get_engine,
    JSONMySQLException,
)
from app.utils import (
    JSONParser,
    flatten_json,
    normalize_nested,
    to_dataframe,
    SchemaInferencer,
)
from app.loaders import (
    BaseLoader,
    LoadResult,
    QuickLoader,
)
from app.validators import DataValidator, ReferentialValidator

__all__ = [
    'setup_logger',
    'get_logger',
    'DatabaseManager',
    'get_engine',
    'JSONMySQLException',
    'JSONParser',
    'flatten_json',
    'normalize_nested',
    'to_dataframe',
    'SchemaInferencer',
    'BaseLoader',
    'LoadResult',
    'QuickLoader',
    'DataValidator',
    'ReferentialValidator',
]
