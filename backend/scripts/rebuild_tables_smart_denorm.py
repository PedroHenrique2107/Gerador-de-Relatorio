#!/usr/bin/env python3
"""
Rebuild tables com desagrupamento INTELIGENTE sem exceder limite de linhas.

Estratégia:
1. Manter todas as colunas base
2. Desagrupar paymentTerm (objeto simples): paymentTerm_id, paymentTerm_description
3. Armazenar receipts como JSON + receipts_count
4. Armazenar receiptsCategories como JSON + receiptsCategories_count
"""

import json
import sys
from pathlib import Path
from sqlalchemy import text

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import DatabaseManager
from app.core.logger import setup_logger
from app.loaders.quick_loader import QuickLoader

logger = setup_logger("rebuild_smart_denorm")


def flatten_record(record):
    """Desagrupar registro mantendo estrutura inteligente."""
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
            # Array: contar + guardar como JSON
            if isinstance(value, list):
                flattened["receipts_count"] = len(value)
                flattened["receipts"] = json.dumps(value) if value else None
            else:
                flattened["receipts_count"] = 0
                flattened["receipts"] = None
                
        elif key == "receiptsCategories":
            # Array: contar + guardar como JSON
            if isinstance(value, list):
                flattened["receiptsCategories_count"] = len(value)
                flattened["receiptsCategories"] = json.dumps(value) if value else None
            else:
                flattened["receiptsCategories_count"] = 0
                flattened["receiptsCategories"] = None
                
        else:
            # Outras colunas: manter como estão
            flattened[key] = value
    
    return flattened


def rebuild_table_from_json(file_path, table_name):
    """Reconstruir tabela a partir do JSON."""
    logger.info(f"Lendo JSON: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # JSON structure: {"data": [...]}
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
        flattened = flatten_record(record)
        flattened_data.append(flattened)
        if (i + 1) % 1000 == 0:
            logger.info(f"  ✓ {i + 1} registros processados...")
    
    logger.info(f"Desagrupamento concluido: {len(flattened_data)} registros")
    
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
    logger.info("RECONSTRUINDO TABELAS COM DESAGRUPAMENTO INTELIGENTE")
    logger.info("=" * 60)
    
    # Initialize database
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_user = os.getenv('MYSQL_USER', 'dev_pricing')
    db_pass = os.getenv('MYSQL_PASSWORD', 'Smart123!@#')
    db_name = os.getenv('MYSQL_DATABASE', 'dev_pricing')
    
    # Escapar caracteres especiais na senha
    from urllib.parse import quote_plus
    db_pass_encoded = quote_plus(db_pass)
    
    database_url = f'mysql+pymysql://{db_user}:{db_pass_encoded}@{db_host}:{db_port}/{db_name}'
    DatabaseManager.initialize(database_url)
    
    confirmation = input("\nAviso: Isso vai deletar as tabelas atuais e recriar com dados processados.\nDeseja continuar? (s/n): ").strip().lower()
    
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
    logger.info("RECONSTRUCAO CONCLUIDA")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
