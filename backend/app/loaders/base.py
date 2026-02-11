"""
Base abstrata para loaders.

Define interface que todos os loaders devem implementar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
from datetime import datetime


@dataclass
class LoadResult:
    """Resultado de um carregamento."""
    success: bool
    table: str
    rows_inserted: int
    rows_failed: int
    execution_time: float
    errors: List[str]
    started_at: datetime
    finished_at: datetime
    
    @property
    def success_rate(self) -> float:
        """Percentual de sucesso."""
        total = self.rows_inserted + self.rows_failed
        if total == 0:
            return 0.0
        return (self.rows_inserted / total) * 100
    
    def __str__(self) -> str:
        """Representação em string."""
        return (
            f"✓ {self.table}: {self.rows_inserted} registros "
            f"({self.success_rate:.1f}% sucesso) em {self.execution_time:.2f}s"
        )


class BaseLoader(ABC):
    """Classe base para todos os loaders."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa loader.
        
        Args:
            config: Configurações específicas do loader
        """
        self.config = config or {}
        self.logger = self._get_logger()
    
    @staticmethod
    def _get_logger():
        """Retorna logger."""
        from app.core import get_logger
        return get_logger(__name__)
    
    @abstractmethod
    def load(
        self,
        file_path: Path,
        table_name: str,
        **kwargs,
    ) -> LoadResult:
        """
        Carrega arquivo JSON para tabela MySQL.
        
        Args:
            file_path: Caminho do arquivo JSON
            table_name: Nome da tabela
            **kwargs: Argumentos específicos do loader
        
        Returns:
            LoadResult: Resultado do carregamento
        
        Raises:
            LoaderError: Se falhar
        """
        pass
    
    @staticmethod
    def _prepare_dataframe(
        df: pd.DataFrame,
        rename_map: Optional[Dict[str, str]] = None,
        select_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Prepara DataFrame para inserção.
        
        Args:
            df: DataFrame original
            rename_map: Mapear nomes de colunas
            select_columns: Selecionar apenas estas colunas
        
        Returns:
            pd.DataFrame: DataFrame preparado
        """
        # Renomeia colunas se necessário
        if rename_map:
            df = df.rename(columns=rename_map)
        
        # Seleciona colunas
        if select_columns:
            df = df[[col for col in select_columns if col in df.columns]]
        
        # Remove colunas vazias
        df = df.dropna(axis=1, how='all')
        
        # Converte NaN para None (MySQL NULL)
        df = df.where(pd.notna(df), None)
        
        return df
    
    @staticmethod
    def _get_chunk_size(config: Dict[str, Any], default: int = 5000) -> int:
        """Retorna tamanho do chunk."""
        return config.get('chunk_size', default)
