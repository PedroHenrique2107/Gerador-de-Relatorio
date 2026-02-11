"""
Denormalizador de JSON para estrutura relacional.

Converte estruturas JSON aninhadas em tabelas relacionais com chaves estrangeiras.
"""

import json
from pathlib import Path
from typing import Tuple, List, Dict, Any
from uuid import uuid4


class JSONDenormalizer:
    """Converte JSON aninhado em estrutura relacional."""
    
    def __init__(self):
        """Inicializa denormalizador."""
        self.tables: Dict[str, List[Dict]] = {}
        self.primary_table_name: str = ""
    
    def denormalize(self, file_path: Path, base_table_name: str) -> Dict[str, List[Dict]]:
        """
        Denormaliza arquivo JSON em múltiplas tabelas.
        
        Args:
            file_path: Caminho do arquivo JSON
            base_table_name: Nome da tabela principal
        
        Returns:
            Dicionário com {table_name: [rows]}
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrai dados se estão em chave 'data'
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        
        # Garante que é uma lista
        if not isinstance(data, list):
            data = [data]
        
        self.tables = {}
        self.primary_table_name = base_table_name
        
        # Processa cada item
        for item in data:
            self._process_item(item, base_table_name, None)
        
        return self.tables
    
    def _process_item(self, item: Dict, table_name: str, parent_id: str = None):
        """
        Processa um item, separando dados aninhados em tabelas.
        
        Args:
            item: Dicionário do item
            table_name: Nome da tabela atual
            parent_id: ID da linha pai (para chaves estrangeiras)
        """
        if table_name not in self.tables:
            self.tables[table_name] = []
        
        # Gera ID para este item
        item_id = str(uuid4())
        flat_item = {'_id': item_id}
        
        # Processa cada campo
        for key, value in item.items():
            if isinstance(value, dict):
                # Campo é um objeto - cria tabela relacionada
                related_table = f"{table_name}_{key}"
                self._process_dict(value, related_table, item_id, table_name)
                # Não inclui no item principal, apenas a chave estrangeira
                flat_item[f"_fk_{key}_id"] = item_id
            
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Campo é array de objetos - cria tabela relacionada
                related_table = f"{table_name}_{key}"
                for sub_item in value:
                    self._process_dict(sub_item, related_table, item_id, table_name)
                # Não inclui no item principal
            
            else:
                # Campo simples - inclui no item
                flat_item[key] = value
        
        # Adiciona chave estrangeira se tem pai
        if parent_id:
            flat_item['_parent_id'] = parent_id
        
        self.tables[table_name].append(flat_item)
    
    def _process_dict(self, sub_item: Dict, table_name: str, parent_id: str, parent_table: str):
        """
        Processa um dicionário aninhado.
        
        Args:
            sub_item: Dicionário a processar
            table_name: Nome da tabela para este item
            parent_id: ID do item pai
            parent_table: Nome da tabela pai
        """
        if table_name not in self.tables:
            self.tables[table_name] = []
        
        sub_id = str(uuid4())
        flat_sub = {'_id': sub_id, '_parent_id': parent_id}
        
        for key, value in sub_item.items():
            if isinstance(value, (dict, list)):
                # Aninhamento profundo - converte para JSON string
                flat_sub[key] = json.dumps(value, ensure_ascii=False)
            else:
                flat_sub[key] = value
        
        self.tables[table_name].append(flat_sub)


def denormalize_json_file(file_path: Path, base_table_name: str) -> Dict[str, List[Dict]]:
    """
    Função helper para denormalizar um arquivo JSON.
    
    Args:
        file_path: Caminho do arquivo JSON
        base_table_name: Nome da tabela principal
    
    Returns:
        Dicionário com {table_name: [rows]}
    """
    denormalizer = JSONDenormalizer()
    return denormalizer.denormalize(file_path, base_table_name)
