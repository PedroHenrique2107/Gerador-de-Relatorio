#!/usr/bin/env python
"""
Script para desagrupar colunas JSON já existentes no banco de dados.

Transforma dados agrupados em estrutura relacional desnormalizada.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# ⚠️ VALIDA VIRTUAL ENVIRONMENT
if 'VIRTUAL_ENV' not in os.environ and not hasattr(sys, 'real_prefix') and sys.prefix == sys.base_prefix:
    error_msg = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌ ERRO: VIRTUAL ENVIRONMENT NÃO ATIVADO               ║
╚════════════════════════════════════════════════════════════════════════════╝

Execute primeiro:
   Windows: .venv\\Scripts\\activate
   macOS/Linux: source .venv/bin/activate
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application import JSONMySQLApplication, ApplicationConfig
from app.core import setup_logger, DatabaseManager
from sqlalchemy import text
import pandas as pd

logger = setup_logger('migrate_denorm')


class ColumnDenormalizer:
    """Desagrupa colunas JSON em tabelas relacionadas."""
    
    def __init__(self, engine):
        """Inicializa denormalizador."""
        self.engine = engine
    
    def denormalize_column(self, table_name: str, column_name: str, child_table_name: str) -> int:
        """
        Desagrupa uma coluna JSON em uma tabela relacionada.
        
        Args:
            table_name: Nome da tabela com dados agrupados
            column_name: Nome da coluna a desagrupar
            child_table_name: Nome da nova tabela relacionada
        
        Returns:
            Número de linhas inseridas
        """
        print(f"\n   📊 Desagrupando: {table_name}.{column_name} → {child_table_name}")
        
        try:
            # Lê dados da tabela principal
            query = text(f"SELECT * FROM {table_name}")
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            print(f"      Lidas {len(df)} linhas da tabela principal")
            
            # Processa cada linha
            child_rows = []
            main_rows_updates = []
            
            for idx, row in df.iterrows():
                row_id = row.get('id') or idx
                col_value = row.get(column_name)
                
                if not col_value or pd.isna(col_value):
                    continue
                
                # Tenta parsear como JSON
                try:
                    if isinstance(col_value, str):
                        data = json.loads(col_value)
                    else:
                        data = col_value
                    
                    # Se é array, processa cada item
                    if isinstance(data, list):
                        for sub_idx, sub_item in enumerate(data):
                            if isinstance(sub_item, dict):
                                child_row = {
                                    f'{table_name}_id': row_id,
                                    '_index': sub_idx
                                }
                                # Achata o sub_item
                                for key, value in sub_item.items():
                                    if isinstance(value, (dict, list)):
                                        child_row[key] = json.dumps(value, ensure_ascii=False)
                                    else:
                                        child_row[key] = value
                                child_rows.append(child_row)
                    
                    # Se é objeto simples, desagrupa direto
                    elif isinstance(data, dict):
                        child_row = {f'{table_name}_id': row_id}
                        for key, value in data.items():
                            if isinstance(value, (dict, list)):
                                child_row[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                child_row[key] = value
                        child_rows.append(child_row)
                
                except json.JSONDecodeError:
                    print(f"      ⚠️ Não foi possível parsear JSON na linha {row_id}")
                    continue
            
            if not child_rows:
                print(f"      ⚠️ Nenhum dado para desagrupar")
                return 0
            
            # Cria tabela relacionada se não existir
            self._create_child_table(child_table_name, child_rows[0])
            
            # Insere dados na tabela relacionada
            child_df = pd.DataFrame(child_rows)
            with self.engine.connect() as conn:
                child_df.to_sql(child_table_name, conn, if_exists='append', index=False)
                conn.commit()
            
            print(f"      ✅ {len(child_rows)} linhas inseridas em {child_table_name}")
            
            # Remove coluna da tabela principal
            with self.engine.connect() as conn:
                drop_col = text(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                conn.execute(drop_col)
                conn.commit()
            
            print(f"      ✓ Coluna removida de {table_name}")
            
            return len(child_rows)
        
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return 0
    
    def _create_child_table(self, table_name: str, sample_row: dict):
        """Cria tabela relacionada se não existir."""
        try:
            # Verifica se tabela existe
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT 1 FROM information_schema.TABLES WHERE TABLE_NAME = '{table_name}'")
                ).fetchone()
            
            if result:
                print(f"      ℹ️ Tabela {table_name} já existe")
                return
            
            # Constrói CREATE TABLE a partir do sample
            columns = []
            for key, value in sample_row.items():
                if key.endswith('_id'):
                    columns.append(f"{key} VARCHAR(36)")
                elif key == '_index':
                    columns.append(f"{key} INT")
                elif isinstance(value, (int, float)):
                    columns.append(f"{key} FLOAT")
                else:
                    columns.append(f"{key} LONGTEXT")
            
            create_sql = f"""
            CREATE TABLE {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(columns)},
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            
            print(f"      ✓ Tabela {table_name} criada")
        
        except Exception as e:
            print(f"      ⚠️ Erro ao criar tabela: {e}")


def migrate_table(table_name: str, columns_to_denormalize: list):
    """
    Migra uma tabela denormalizando as colunas especificadas.
    
    Args:
        table_name: Nome da tabela
        columns_to_denormalize: Lista de (column_name, child_table_name)
    """
    print(f"\n{'='*70}")
    print(f"🔄 MIGRANDO TABELA: {table_name}")
    print(f"{'='*70}")
    
    app_config = ApplicationConfig()
    app = JSONMySQLApplication(app_config)
    denormalizer = ColumnDenormalizer(DatabaseManager.get_engine())
    
    total_rows = 0
    
    for column_name, child_table_name in columns_to_denormalize:
        rows = denormalizer.denormalize_column(table_name, column_name, child_table_name)
        total_rows += rows
    
    print(f"\n✅ Migração concluída")
    print(f"   Total de linhas desagrupadas: {total_rows}")


def main():
    """Função principal."""
    try:
        print("\n" + "="*70)
        print("🔄 DESAGRUPADOR DE COLUNAS JSON")
        print("="*70)
        print("\nEste script desagrupa colunas JSON em tabelas relacionadas")
        print("sem perder nenhum dado.\n")
        
        # Define migrações
        migrations = [
            {
                'table': 'parcelas_contareceber_datacompetparcelas',
                'columns': [
                    ('paymentTerm', 'parcelas_contareceber_datacompetparcelas_paymentterm'),
                    ('receipts', 'parcelas_contareceber_datacompetparcelas_receipts'),
                    ('receiptsCategories', 'parcelas_contareceber_datacompetparcelas_receiptscategories'),
                ]
            },
            {
                'table': 'parcelas_contareceber_datapagtoparcelas',
                'columns': [
                    ('paymentTerm', 'parcelas_contareceber_datapagtoparcelas_paymentterm'),
                    ('receipts', 'parcelas_contareceber_datapagtoparcelas_receipts'),
                    ('receiptsCategories', 'parcelas_contareceber_datapagtoparcelas_receiptscategories'),
                ]
            }
        ]
        
        print("Tabelas a processar:")
        for i, migration in enumerate(migrations, 1):
            print(f"{i}. {migration['table']}")
            for col, child in migration['columns']:
                print(f"   - {col} → {child}")
        
        print("\n" + "-"*70)
        response = input("Deseja continuar com a migração? (s/n): ").strip().lower()
        
        if response != 's':
            print("Operação cancelada.")
            return
        
        # Executa migrações
        for migration in migrations:
            migrate_table(migration['table'], migration['columns'])
        
        print("\n" + "="*70)
        print("✨ Todas as migrações foram concluídas com sucesso!")
        print("="*70)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
