"""
Denormalizador profundo de JSON para estrutura relacional plana.

Converte objetos aninhados em colunas separadas com prefixos.
Exemplo: paymentTerm.id → paymentTerm_id
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd


class CompleteFlattener:
    """Faz flattening completo sem agrupamentos."""
    
    def __init__(self, max_depth: int = 3):
        """
        Inicializa o flattener.
        
        Args:
            max_depth: Profundidade máxima para flattening
        """
        self.max_depth = max_depth
        self.array_tables: Dict[str, List[Dict]] = {}
    
    def flatten_object(self, obj: Dict, prefix: str = '', depth: int = 0) -> Dict:
        """
        Achata um objeto, convertendo campos aninhados em colunas.
        
        Args:
            obj: Objeto a achatar
            prefix: Prefixo das colunas
            depth: Profundidade atual
        
        Returns:
            Dicionário achatado
        """
        result = {}
        
        for key, value in obj.items():
            col_name = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                # Objeto aninhado - achata com prefixo
                if depth < self.max_depth:
                    nested_flat = self.flatten_object(value, col_name, depth + 1)
                    result.update(nested_flat)
                else:
                    # Se ultrapassou profundidade, converte para string
                    result[col_name] = json.dumps(value, ensure_ascii=False)
            
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Array de objetos - será colocado em tabela separada
                    # Por enquanto, apenas armazena o count
                    result[f"{col_name}_count"] = len(value)
                else:
                    # Array simples - converte para string
                    result[col_name] = json.dumps(value, ensure_ascii=False)
            
            else:
                # Valor simples
                result[col_name] = value
        
        return result
    
    def process_arrays(self, rows: List[Dict], base_table_name: str) -> Dict[str, List[Dict]]:
        """
        Processa arrays aninhados, criando tabelas separadas.
        
        Args:
            rows: Linhas processadas
            base_table_name: Nome da tabela base
        
        Returns:
            Dicionário com {table_name: [rows]}
        """
        tables = {base_table_name: rows}
        
        # Para cada linha, processa os arrays originais
        for idx, row in enumerate(rows):
            # Procura por arrays na estrutura original
            # Isso será feito melhor reconstruindo a estrutura
            pass
        
        return tables
    
    def denormalize_file(self, file_path: Path, base_table_name: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Denormaliza arquivo JSON em múltiplos DataFrames.
        
        Args:
            file_path: Caminho do arquivo JSON
            base_table_name: Nome da tabela base
        
        Returns:
            (df_principal, {table_name: df})
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrai dados se estão em chave 'data'
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        
        if not isinstance(data, list):
            data = [data]
        
        # Processa cada item, gerando tabelas relacionadas
        main_rows = []
        related_tables = {}
        
        for item_idx, item in enumerate(data):
            # Faz deep copy para processar
            processed_item, related_data = self._process_item_deep(
                item, base_table_name, item_idx
            )
            main_rows.append(processed_item)
            
            # Mescla dados relacionados
            for table_name, related_rows in related_data.items():
                if table_name not in related_tables:
                    related_tables[table_name] = []
                related_tables[table_name].extend(related_rows)
        
        # Converte para DataFrames
        main_df = pd.DataFrame(main_rows)
        other_dfs = {name: pd.DataFrame(rows) for name, rows in related_tables.items()}
        
        return main_df, other_dfs
    
    def _process_item_deep(self, item: Dict, base_table_name: str, item_idx: int) -> Tuple[Dict, Dict]:
        """
        Processa um item profundamente, extraindo arrays em tabelas separadas.
        
        Returns:
            (main_item, {table_name: [related_rows]})
        """
        main_item = {}
        related_tables = {}
        parent_id = f"{base_table_name}_{item_idx}"
        
        for key, value in item.items():
            if isinstance(value, dict):
                # Objeto simples - achata com prefixo
                for sub_key, sub_value in value.items():
                    col_name = f"{key}_{sub_key}"
                    if isinstance(sub_value, (dict, list)):
                        main_item[col_name] = json.dumps(sub_value, ensure_ascii=False)
                    else:
                        main_item[col_name] = sub_value
            
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Array de objetos - cria tabela relacionada
                    table_name = f"{base_table_name}_{key}"
                    related_rows = []
                    
                    for sub_idx, sub_item in enumerate(value):
                        row = {'_parent_id': parent_id, '_index': sub_idx}
                        
                        # Achata os itens da lista
                        for sub_key, sub_value in sub_item.items():
                            if isinstance(sub_value, (dict, list)):
                                row[sub_key] = json.dumps(sub_value, ensure_ascii=False)
                            else:
                                row[sub_key] = sub_value
                        
                        related_rows.append(row)
                    
                    if related_rows:
                        related_tables[table_name] = related_rows
                    main_item[f"{key}_count"] = len(value)
                
                else:
                    # Array simples - converte para string
                    main_item[key] = json.dumps(value, ensure_ascii=False)
            
            else:
                # Valor simples
                main_item[key] = value
        
        return main_item, related_tables


def denormalize_json_file(file_path: Path, base_table_name: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Função helper para denormalizar um arquivo JSON.
    
    Args:
        file_path: Caminho do arquivo JSON
        base_table_name: Nome da tabela principal
    
    Returns:
        (df_principal, {table_name: df})
    """
    flattener = CompleteFlattener()
    return flattener.denormalize_file(file_path, base_table_name)
