"""
Utilitários para gerenciamento de schema e tipos de dados.

Infere tipos de dados automaticamente a partir de dados.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, BIGINT, JSON
)
from sqlalchemy.types import TypeEngine
from app.core.logger import get_logger
from datetime import datetime, date

logger = get_logger(__name__)


class SchemaInferencer:
    """Infere schema SQL a partir de dados."""
    
    # Mapeamento de tipos Python → SQLAlchemy
    TYPE_MAP = {
        'int64': BIGINT,
        'int32': Integer,
        'float64': Float,
        'object': String,
        'bool': Boolean,
        'datetime64[ns]': DateTime,
    }
    
    @staticmethod
    def infer_types(df: pd.DataFrame) -> Dict[str, str]:
        """
        Infere tipos de dados de um DataFrame.
        
        Args:
            df: DataFrame com dados
        
        Returns:
            Dict[str, str]: {coluna: tipo_sql}
        """
        types = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            types[col] = SchemaInferencer._map_type(dtype, df[col])
        
        return types
    
    @staticmethod
    def _map_type(dtype: str, series: pd.Series) -> str:
        """Mapeia dtype pandas para tipo SQL."""
        
        # Tipos numéricos
        if 'int' in dtype:
            max_val = series.max()
            if pd.notna(max_val):
                if max_val > 2**31:
                    return 'BIGINT(20)'
                return 'INT(11)'
            return 'INT(11)'
        
        if 'float' in dtype:
            return 'DOUBLE'
        
        if 'bool' in dtype:
            return 'BOOLEAN'
        
        # Datas
        if 'datetime' in dtype:
            return 'DATETIME'
        
        if 'date' in dtype:
            return 'DATE'
        
        # Strings
        if 'object' in dtype:
            # Calcula tamanho máximo
            try:
                max_len = series.astype(str).str.len().max()
                if pd.notna(max_len):
                    if max_len < 256:
                        return f'VARCHAR({int(max_len) + 10})'
                    elif max_len < 65536:
                        return 'TEXT'
                    else:
                        return 'LONGTEXT'
            except:
                pass
            return 'VARCHAR(255)'
        
        # JSON
        if 'json' in dtype.lower():
            return 'JSON'
        
        # Padrão
        return 'VARCHAR(255)'
    
    @staticmethod
    def generate_create_table(
        table_name: str,
        df: pd.DataFrame,
        primary_key: Optional[str] = None,
        indexes: Optional[List[str]] = None,
    ) -> str:
        """
        Gera comando CREATE TABLE.
        
        Args:
            table_name: Nome da tabela
            df: DataFrame com dados
            primary_key: Nome da coluna chave primária
            indexes: Colunas para criar índices
        
        Returns:
            str: Comando SQL CREATE TABLE
        """
        types = SchemaInferencer.infer_types(df)
        
        columns = []
        
        # ID auto-increment como PK por padrão
        columns.append(
            "id BIGINT AUTO_INCREMENT PRIMARY KEY"
        )
        
        # Colunas do DataFrame
        for col, dtype in types.items():
            col_sql = f"`{col}` {dtype}"
            
            # Permite NULL por padrão (exceto chaves)
            if not col.endswith('Id'):
                col_sql += " NULL"
            
            columns.append(col_sql)
        
        # Timestamps
        columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        
        # Índices
        if indexes:
            for col in indexes:
                columns.append(f"INDEX idx_{table_name}_{col} (`{col}`)")
        
        sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
        sql += ",\n".join(f"  {col}" for col in columns)
        sql += f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        
        return sql


def create_column_spec(
    name: str,
    dtype: str,
    nullable: bool = True,
    index: bool = False,
) -> str:
    """
    Cria especificação de coluna SQL.
    
    Args:
        name: Nome da coluna
        dtype: Tipo de dado (VARCHAR, INT, etc)
        nullable: Permite NULL
        index: Criar índice
    
    Returns:
        str: Especificação de coluna
    """
    spec = f"`{name}` {dtype}"
    
    if not nullable:
        spec += " NOT NULL"
    
    return spec


def validate_schema_match(
    df: pd.DataFrame,
    table_schema: Dict[str, str],
) -> Tuple[bool, List[str]]:
    """
    Valida se DataFrame corresponde ao schema da tabela.
    
    Args:
        df: DataFrame
        table_schema: {coluna: tipo}
    
    Returns:
        Tuple[bool, List[str]]: (válido, erros)
    """
    errors = []
    
    # Verifica colunas faltantes
    df_cols = set(df.columns)
    schema_cols = set(table_schema.keys())
    
    missing = schema_cols - df_cols
    if missing:
        errors.append(f"Colunas faltantes: {missing}")
    
    extra = df_cols - schema_cols
    if extra:
        errors.append(f"Colunas extras: {extra}")
    
    return len(errors) == 0, errors
