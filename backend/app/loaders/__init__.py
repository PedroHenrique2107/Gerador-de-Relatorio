"""
Init do módulo loaders.
"""

from app.loaders.base import BaseLoader, LoadResult
from app.loaders.quick_loader import QuickLoader

__all__ = [
    'BaseLoader',
    'LoadResult',
    'QuickLoader',
]
