"""
Validators para dados e schema.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
from app.core.logger import get_logger
from app.core.exceptions import ValidationError

logger = get_logger(__name__)


class DataValidator:
    """Valida integridade de dados."""
    
    @staticmethod
    def validate_no_nulls(
        df: pd.DataFrame,
        required_columns: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Valida que colunas obrigatórias não têm NULL.
        
        Args:
            df: DataFrame
            required_columns: Colunas que não podem ser NULL
        
        Returns:
            Tuple[bool, List[str]]: (válido, erros)
        """
        errors = []
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Coluna obrigatória faltando: {col}")
            elif df[col].isnull().any():
                null_count = df[col].isnull().sum()
                errors.append(f"Coluna '{col}' tem {null_count} NULLs")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_unique(
        df: pd.DataFrame,
        columns: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Valida que combinação de colunas é única.
        
        Args:
            df: DataFrame
            columns: Colunas para validar uniqueness
        
        Returns:
            Tuple[bool, List[str]]: (válido, erros)
        """
        errors = []
        
        duplicates = df.duplicated(subset=columns, keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            errors.append(f"{dup_count} registros duplicados em {columns}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_range(
        df: pd.DataFrame,
        column: str,
        min_val: float,
        max_val: float,
    ) -> Tuple[bool, List[str]]:
        """
        Valida que coluna está dentro de range.
        
        Args:
            df: DataFrame
            column: Nome da coluna
            min_val: Valor mínimo
            max_val: Valor máximo
        
        Returns:
            Tuple[bool, List[str]]: (válido, erros)
        """
        errors = []
        
        if column not in df.columns:
            errors.append(f"Coluna não existe: {column}")
        else:
            out_of_range = (df[column] < min_val) | (df[column] > max_val)
            if out_of_range.any():
                count = out_of_range.sum()
                errors.append(
                    f"{count} valores fora do range [{min_val}, {max_val}] em {column}"
                )
        
        return len(errors) == 0, errors


class ReferentialValidator:
    """Valida integridade referencial."""
    
    @staticmethod
    def validate_foreign_key(
        child_df: pd.DataFrame,
        child_column: str,
        parent_df: pd.DataFrame,
        parent_column: str,
    ) -> Tuple[bool, List[str]]:
        """
        Valida que chaves estrangeiras existem na tabela pai.
        
        Args:
            child_df: DataFrame filho
            child_column: Coluna da chave estrangeira
            parent_df: DataFrame pai
            parent_column: Coluna da chave primária
        
        Returns:
            Tuple[bool, List[str]]: (válido, erros)
        """
        errors = []
        
        if child_column not in child_df.columns:
            errors.append(f"Coluna FK não existe: {child_column}")
        elif parent_column not in parent_df.columns:
            errors.append(f"Coluna PK não existe: {parent_column}")
        else:
            # Verifica se todos os FKs existem no parent
            parent_values = set(parent_df[parent_column].unique())
            child_values = child_df[child_column].dropna().unique()
            
            orphans = set(child_values) - parent_values
            if orphans:
                errors.append(
                    f"{len(orphans)} registros órfãos em {child_column}"
                )
        
        return len(errors) == 0, errors
