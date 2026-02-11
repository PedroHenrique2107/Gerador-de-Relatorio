"""
Utilitários para processamento de JSON.

Suporta NDJSON, JSON Array e JSON aninhado.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Any, Iterator, Dict, List, Union, Optional
from app.core.logger import get_logger
from app.core.exceptions import ParsingError, InvalidFormatError

logger = get_logger(__name__)


class JSONParser:
    """Parser flexível para JSON em vários formatos."""
    
    @staticmethod
    def parse_file(
        file_path: Union[str, Path],
        lines: bool = False,
        sample_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse JSON de arquivo.
        
        Args:
            file_path: Caminho do arquivo
            lines: Se True, trata como NDJSON (uma linha por JSON)
            sample_size: Se definido, retorna apenas primeiras N linhas
        
        Returns:
            List[Dict]: Lista de objetos
        
        Raises:
            FileNotFoundError: Se arquivo não existe
            ParsingError: Se JSON inválido
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        logger.info(f"Parsando arquivo JSON: {file_path}")
        
        try:
            if lines:
                return JSONParser._parse_ndjson(file_path, sample_size)
            else:
                return JSONParser._parse_json_array(file_path, sample_size)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Erro ao fazer parsing de JSON: {e}")
        except Exception as e:
            raise ParsingError(f"Erro inesperado: {e}")
    
    @staticmethod
    def _parse_ndjson(
        file_path: Path,
        sample_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Parse NDJSON (newline-delimited JSON)."""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if sample_size and i >= sample_size:
                    break
                if line.strip():
                    data.append(json.loads(line))
        logger.info(f"✓ NDJSON: {len(data)} registros")
        return data
    
    @staticmethod
    def _parse_json_array(
        file_path: Path,
        sample_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Parse JSON Array (lista) ou objeto com chave 'data'."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Suporta wrapper {"data": [...]}
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        if not isinstance(data, list):
            raise InvalidFormatError(
                "JSON deve ser um array de objetos ou um objeto com chave 'data' contendo um array"
            )
        
        if sample_size:
            data = data[:sample_size]
        
        logger.info(f"✓ JSON Array: {len(data)} registros")
        return data
    
    @staticmethod
    def iterate_file(
        file_path: Union[str, Path],
        lines: bool = False,
        chunk_size: int = 5000,
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Itera arquivo em chunks para economizar memória.
        
        Args:
            file_path: Caminho do arquivo
            lines: Se True, trata como NDJSON
            chunk_size: Tamanho de cada chunk
        
        Yields:
            List[Dict]: Chunks de dados
        """
        file_path = Path(file_path)
        chunk = []
        
        try:
            if lines:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            chunk.append(json.loads(line))
                            if len(chunk) >= chunk_size:
                                yield chunk
                                chunk = []
            else:
                # JSON array - lê tudo e itera em chunks
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Suporta wrapper {"data": [...]}
                if isinstance(data, dict) and "data" in data:
                    data = data["data"]

                if not isinstance(data, list):
                    raise InvalidFormatError(
                        "JSON deve ser um array de objetos ou um objeto com chave 'data' contendo um array"
                    )

                for i in range(0, len(data), chunk_size):
                    yield data[i:i + chunk_size]
                return
            
            # Yield último chunk
            if chunk:
                yield chunk
        
        except Exception as e:
            logger.error(f"Erro ao iterar arquivo: {e}")
            raise ParsingError(str(e))


def flatten_json(
    data: Dict[str, Any],
    parent_key: str = '',
    separator: str = '_',
) -> Dict[str, Any]:
    """
    Achata JSON aninhado.
    
    Exemplo:
        >>> data = {'a': {'b': 1, 'c': 2}, 'd': 3}
        >>> flatten_json(data)
        {'a_b': 1, 'a_c': 2, 'd': 3}
    
    Args:
        data: Dict aninhado
        parent_key: Prefixo da chave
        separator: Separador entre chaves
    
    Returns:
        Dict: JSON achatado
    """
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(
                flatten_json(value, new_key, separator).items()
            )
        elif isinstance(value, list):
            # Para listas, cria separador com índice
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.extend(
                        flatten_json(item, f"{new_key}_{i}", separator).items()
                    )
                else:
                    items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, value))
    
    return dict(items)


def normalize_nested(
    data: List[Dict[str, Any]],
    nested_fields: Dict[str, str],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Normaliza campos JSON aninhados em tabelas separadas.
    
    Exemplo:
        >>> data = [
        ...     {
        ...         'id': 1,
        ...         'items': [{'item_id': 1, 'qty': 5}, {'item_id': 2, 'qty': 3}]
        ...     }
        ... ]
        >>> normalize_nested(data, {'items': 'Orders'})
        {
            'main': [{'id': 1}],
            'Orders': [
                {'id': 1, 'item_id': 1, 'qty': 5},
                {'id': 1, 'item_id': 2, 'qty': 3}
            ]
        }
    
    Args:
        data: Lista de dicts com campos aninhados
        nested_fields: {campo_aninhado: nome_tabela}
    
    Returns:
        Dict[str, List]: {tabela: [registros]}
    """
    main_data = []
    normalized = {'main': []}
    
    # Inicializa dicts para cada tabela aninhada
    for table_name in nested_fields.values():
        normalized[table_name] = []
    
    # Processa cada registro
    for record in data:
        main_record = record.copy()
        pk_values = {}
        
        # Salva chaves primárias
        for key in ['id', 'billId', 'customerId', 'orderId']:
            if key in record:
                pk_values[key] = record[key]
        
        # Processa campos aninhados
        for nested_field, table_name in nested_fields.items():
            if nested_field in record:
                nested_data = record.pop(nested_field)
                
                # Se for lista, cria registros filhos
                if isinstance(nested_data, list):
                    for nested_item in nested_data:
                        child_record = {**pk_values, **nested_item}
                        normalized[table_name].append(child_record)
        
        main_data.append(main_record)
    
    normalized['main'] = main_data
    return normalized


def to_dataframe(data: Union[List[Dict], Dict]) -> pd.DataFrame:
    """
    Converte dados para pandas DataFrame.
    
    Args:
        data: Lista de dicts ou dict de listas
    
    Returns:
        pd.DataFrame: DataFrame normalizado
    """
    return pd.DataFrame(data)
