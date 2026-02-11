#!/usr/bin/env python
"""
Script para reconstruir tabelas com desagrupamento correto.

1. Deleta as tabelas
2. Recarrega dados do JSON com desagrupamento na mesma tabela
"""

import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application import ApplicationConfig, JSONMySQLApplication
from app.core import setup_logger, DatabaseManager
from sqlalchemy import text
import json
import pandas as pd

logger = setup_logger('rebuild_tables')


def rebuild_table_from_json(file_path: Path, table_name: str):
    """
    Reconstrói tabela a partir do JSON com desagrupamento na mesma tabela.
    """
    print(f"\n{'='*70}")
    print(f"🔨 RECONSTRUINDO: {table_name}")
    print(f"{'='*70}")
    
    engine = DatabaseManager.get_engine()
    
    # Lê JSON
    print(f"   📖 Lendo: {file_path.name}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'data' in data:
        data = data['data']
    
    if not isinstance(data, list):
        data = [data]
    
    print(f"   ✓ {len(data)} registros carregados")
    
    # Processa dados - desagrupa na mesma tabela
    processed_rows = []
    
    for row in data:
        new_row = {}
        
        for key, value in row.items():
            if key == 'paymentTerm' and isinstance(value, dict):
                # Desagrupa paymentTerm
                for sub_key, sub_value in value.items():
                    new_row[f'paymentTerm_{sub_key}'] = sub_value
            
            elif key == 'receipts' and isinstance(value, list):
                # Para receipts (array), armazena contagem e JSON
                new_row['receipts_count'] = len(value)
                new_row['receipts'] = json.dumps(value, ensure_ascii=False)
                
                # Também desagrupa o primeiro item
                if value and isinstance(value[0], dict):
                    first_receipt = value[0]
                    for sub_key, sub_value in first_receipt.items():
                        if isinstance(sub_value, (dict, list)):
                            new_row[f'receipts_first_{sub_key}'] = json.dumps(sub_value, ensure_ascii=False)
                        else:
                            new_row[f'receipts_first_{sub_key}'] = sub_value
            
            elif key == 'receiptsCategories' and isinstance(value, list):
                # Para receiptsCategories, armazena contagem e desagrupa
                new_row['receiptsCategories_count'] = len(value)
                new_row['receiptsCategories'] = json.dumps(value, ensure_ascii=False)
                
                # Desagrupa cada item
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        for sub_key, sub_value in item.items():
                            if isinstance(sub_value, (dict, list)):
                                new_row[f'receiptsCategories_{idx}_{sub_key}'] = json.dumps(sub_value, ensure_ascii=False)
                            else:
                                new_row[f'receiptsCategories_{idx}_{sub_key}'] = sub_value
            
            elif isinstance(value, (dict, list)):
                # Outros tipos complexos - armazena como JSON
                new_row[key] = json.dumps(value, ensure_ascii=False)
            
            else:
                # Valores simples
                new_row[key] = value
        
        processed_rows.append(new_row)
    
    # Converte para DataFrame
    df = pd.DataFrame(processed_rows)
    
    print(f"   ✓ Dados processados: {len(df)} linhas, {len(df.columns)} colunas")
    print(f"   Colunas: {', '.join(list(df.columns)[:10])}...")
    
    # Deleta tabela antiga
    with engine.connect() as conn:
        try:
            drop_sql = text(f"DROP TABLE {table_name}")
            conn.execute(drop_sql)
            conn.commit()
            print(f"   ✓ Tabela antiga deletada")
        except:
            print(f"   ℹ️ Tabela não existia")
    
    # Cria nova tabela
    print(f"   📝 Criando nova tabela...")
    with engine.connect() as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.commit()
    
    print(f"   ✅ Tabela recriada com sucesso!")
    print(f"   📊 Total de colunas: {len(df.columns)}")


def main():
    try:
        print("\n" + "="*70)
        print("🔨 RECONSTRUTOR DE TABELAS")
        print("="*70)
        
        app_config = ApplicationConfig()
        app = JSONMySQLApplication(app_config)
        
        files_to_rebuild = [
            (Path(__file__).parent.parent / 'data' / 'PARCELAS_CONTARECEBER_DATACOMPETPARCELAS.json',
             'parcelas_contareceber_datacompetparcelas'),
            (Path(__file__).parent.parent / 'data' / 'PARCELAS_CONTARECEBER_DATAPAGTOPARCELAS.json',
             'parcelas_contareceber_datapagtoparcelas'),
        ]
        
        print("\nArquivos a processar:")
        for file_path, table in files_to_rebuild:
            print(f"  - {file_path.name} → {table}")
        
        print("\n" + "-"*70)
        response = input("Deseja continuar? (s/n): ").strip().lower()
        
        if response != 's':
            print("Operação cancelada.")
            return
        
        for file_path, table_name in files_to_rebuild:
            rebuild_table_from_json(file_path, table_name)
        
        print("\n" + "="*70)
        print("✨ Reconstrução concluída!")
        print("="*70)
    
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
