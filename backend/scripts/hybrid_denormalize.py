#!/usr/bin/env python3
"""
Desagrupar com estratégia HÍBRIDA:
- Expandir primeiros N elementos de cada array em colunas
- Armazenar resto como JSON se houver overflow

Estratégia:
- receipts: expande com limite inteligente
- receiptsCategories: expande com limite inteligente
"""

import json
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import DatabaseManager
from app.core.logger import setup_logger

logger = setup_logger("hybrid_denormalize")


def get_array_stats(file_path):
    """Descobrir estatísticas dos arrays."""
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    if isinstance(json_data, dict) and "data" in json_data:
        data = json_data["data"]
    elif isinstance(json_data, list):
        data = json_data
    else:
        raise ValueError(f"Unexpected JSON structure in {file_path}")
    
    receipts_sizes = []
    categories_sizes = []
    receipts_keys = set()
    categories_keys = set()
    
    for record in data:
        if isinstance(record.get("receipts"), list):
            receipts_sizes.append(len(record["receipts"]))
            for item in record["receipts"]:
                if isinstance(item, dict):
                    receipts_keys.update(item.keys())
        
        if isinstance(record.get("receiptsCategories"), list):
            categories_sizes.append(len(record["receiptsCategories"]))
            for item in record["receiptsCategories"]:
                if isinstance(item, dict):
                    categories_keys.update(item.keys())
    
    return {
        "receipts_max": max(receipts_sizes) if receipts_sizes else 0,
        "receipts_avg": sum(receipts_sizes) / len(receipts_sizes) if receipts_sizes else 0,
        "receipts_keys": receipts_keys,
        "categories_max": max(categories_sizes) if categories_sizes else 0,
        "categories_avg": sum(categories_sizes) / len(categories_sizes) if categories_sizes else 0,
        "categories_keys": categories_keys,
    }


def flatten_record(record, max_expand_receipts, max_expand_categories):
    """Desagrupar registro com limite inteligente."""
    flattened = {}
    
    for key, value in record.items():
        if key == "paymentTerm":
            # Desagrupar paymentTerm: objeto simples
            if isinstance(value, dict):
                flattened["paymentTerm_id"] = value.get("id")
                flattened["paymentTerm_description"] = value.get("description")
            else:
                flattened["paymentTerm_id"] = None
                flattened["paymentTerm_description"] = None
                
        elif key == "receipts":
            # Array: contar + expandir apenas os primeiros N
            if isinstance(value, list):
                flattened["receipts_count"] = len(value)
                # Expandir apenas os primeiros max_expand_receipts
                for idx in range(min(len(value), max_expand_receipts)):
                    item = value[idx]
                    if isinstance(item, dict):
                        for prop_key, prop_val in item.items():
                            col_name = f"receipts_{idx}_{prop_key}"
                            # Converter dicts e lists para JSON string
                            if isinstance(prop_val, (dict, list)):
                                flattened[col_name] = json.dumps(prop_val)
                            else:
                                flattened[col_name] = prop_val
                # Se houver mais elementos, armazenar como JSON
                if len(value) > max_expand_receipts:
                    flattened["receipts_extra"] = json.dumps(value[max_expand_receipts:])
            else:
                flattened["receipts_count"] = 0
                
        elif key == "receiptsCategories":
            # Array: contar + expandir apenas os primeiros N
            if isinstance(value, list):
                flattened["receiptsCategories_count"] = len(value)
                # Expandir apenas os primeiros max_expand_categories
                for idx in range(min(len(value), max_expand_categories)):
                    item = value[idx]
                    if isinstance(item, dict):
                        for prop_key, prop_val in item.items():
                            col_name = f"receiptsCategories_{idx}_{prop_key}"
                            # Converter dicts e lists para JSON string
                            if isinstance(prop_val, (dict, list)):
                                flattened[col_name] = json.dumps(prop_val)
                            else:
                                flattened[col_name] = prop_val
                # Se houver mais elementos, armazenar como JSON
                if len(value) > max_expand_categories:
                    flattened["receiptsCategories_extra"] = json.dumps(value[max_expand_categories:])
            else:
                flattened["receiptsCategories_count"] = 0
                
        else:
            # Outras colunas: manter como estão (se for dict/list, converter para JSON)
            if isinstance(value, (dict, list)):
                flattened[key] = json.dumps(value)
            else:
                flattened[key] = value
    
    return flattened


def rebuild_table_from_json(file_path, table_name):
    """Reconstruir tabela a partir do JSON."""
    logger.info(f"Lendo JSON: {file_path}")
    
    # Descobrir estatísticas
    logger.info("Analisando arrays...")
    stats = get_array_stats(file_path)
    logger.info(f"  receipts - max: {stats['receipts_max']}, avg: {stats['receipts_avg']:.1f}, props: {len(stats['receipts_keys'])}")
    logger.info(f"  categories - max: {stats['categories_max']}, avg: {stats['categories_avg']:.1f}, props: {len(stats['categories_keys'])}")
    
    # Definir estratégia de expansão com limite conservador
    # Para evitar exceder 8126 bytes, limitamos a expansão
    max_expand_receipts = min(3, stats['receipts_max'])  # Expandir apenas os 3 primeiros
    max_expand_categories = min(10, stats['categories_max'])  # Expandir até 10
    
    logger.info(f"  Estrategia: expandir receipts={max_expand_receipts}, categories={max_expand_categories}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    if isinstance(json_data, dict) and "data" in json_data:
        data = json_data["data"]
    elif isinstance(json_data, list):
        data = json_data
    else:
        raise ValueError(f"Unexpected JSON structure in {file_path}")
    
    logger.info(f"Total de registros: {len(data)}")
    
    # Desagrupar todos os registros
    flattened_data = []
    for i, record in enumerate(data):
        flattened = flatten_record(record, max_expand_receipts, max_expand_categories)
        flattened_data.append(flattened)
        if (i + 1) % 1000 == 0:
            logger.info(f"  [{i + 1}] registros processados...")
    
    logger.info(f"Desagrupamento concluido: {len(flattened_data)} registros")
    
    # Initialize database
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_user = os.getenv('MYSQL_USER', 'dev_pricing')
    db_pass = os.getenv('MYSQL_PASSWORD', 'Smart123!@#')
    db_name = os.getenv('MYSQL_DATABASE', 'dev_pricing')
    
    from urllib.parse import quote_plus
    db_pass_encoded = quote_plus(db_pass)
    database_url = f'mysql+pymysql://{db_user}:{db_pass_encoded}@{db_host}:{db_port}/{db_name}'
    
    DatabaseManager.initialize(database_url)
    
    # Obter conexão do banco
    db = DatabaseManager()
    engine = DatabaseManager.get_engine()
    
    logger.info(f"Deletando tabela antiga: {table_name}")
    try:
        with db.connection() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
            conn.commit()
            logger.info(f"Tabela deletada")
    except Exception as e:
        logger.error(f"Erro ao deletar tabela: {e}")
        raise
    
    logger.info(f"Inserindo {len(flattened_data)} registros...")
    try:
        import pandas as pd
        df = pd.DataFrame(flattened_data)
        logger.info(f"DataFrame shape: {df.shape[0]} rows x {df.shape[1]} cols")
        
        df.to_sql(
            table_name,
            con=engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=500,
        )
        logger.info(f"Dados inseridos com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inserir dados: {e}")
        raise


def main():
    """Reconstruir ambas as tabelas."""
    files_config = [
        (
            "data/PARCELAS_CONTARECEBER_DATACOMPETPARCELAS.json",
            "parcelas_contareceber_datacompetparcelas"
        ),
        (
            "data/PARCELAS_CONTARECEBER_DATAPAGTOPARCELAS.json",
            "parcelas_contareceber_datapagtoparcelas"
        ),
    ]
    
    logger.info("=" * 60)
    logger.info("DESAGRUPAMENTO HIBRIDO (Expandir + JSON backup)")
    logger.info("=" * 60)
    
    confirmation = input("\nAviso: Isso vai deletar as tabelas atuais e recriar com desagrupamento hibrido.\nDeseja continuar? (s/n): ").strip().lower()
    
    if confirmation != 's':
        logger.info("Operacao cancelada")
        return
    
    for file_path, table_name in files_config:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Processando: {file_path} -> {table_name}")
        logger.info(f"{'=' * 60}")
        
        try:
            if not Path(file_path).exists():
                logger.error(f"Arquivo nao encontrado: {file_path}")
                continue
            
            rebuild_table_from_json(file_path, table_name)
            logger.info(f"SUCESSO: {table_name} recriada com sucesso!\n")
            
        except Exception as e:
            logger.error(f"Erro ao processar {table_name}: {e}\n")
    
    logger.info("=" * 60)
    logger.info("DESAGRUPAMENTO CONCLUIDO")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
