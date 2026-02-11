#!/usr/bin/env python
"""
Script para desagrupar colunas JSON NA MESMA TABELA.

Transforma:
  paymentTerm (JSON) → paymentTerm_id, paymentTerm_description (colunas)
  
Mantém tudo na mesma tabela, sem criar novas tabelas.
"""

import sys
import os
import json
from pathlib import Path

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

logger = setup_logger('flatten_same_table')


class InPlaceFlattener:
    """Desagrupa colunas JSON mantendo na mesma tabela."""
    
    def __init__(self, engine):
        """Inicializa."""
        self.engine = engine
    
    def flatten_column_in_place(self, table_name: str, column_name: str) -> int:
        """
        Desagrupa uma coluna JSON na mesma tabela.
        
        Exemplo:
            paymentTerm: {"id": "PM", "description": "Parcelas"}
            →
            paymentTerm_id: "PM"
            paymentTerm_description: "Parcelas"
            
            receipts: [{"amount": 100}, {"amount": 200}]
            →
            receipts_count: 2
            receipts_data_json: "[{...}, {...}]"  (JSON completo preservado)
        
        Args:
            table_name: Nome da tabela
            column_name: Nome da coluna a desagrupar
        
        Returns:
            Número de colunas adicionadas
        """
        print(f"\n   📊 Desagrupando: {table_name}.{column_name}")
        
        try:
            # Lê todos os dados
            query = text(f"SELECT id, {column_name} FROM {table_name}")
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            print(f"      Lidas {len(df)} linhas")
            
            # Verifica o tipo de dados
            sample_value = None
            for value in df[column_name]:
                if pd.notna(value):
                    try:
                        if isinstance(value, str):
                            sample_value = json.loads(value)
                        else:
                            sample_value = value
                        if sample_value:
                            break
                    except:
                        pass
            
            if not sample_value:
                print(f"      ⚠️ Nenhum dado válido encontrado")
                return 0
            
            # Se é array, apenas faz contagem e preserva JSON
            if isinstance(sample_value, list):
                print(f"      Array detectado - preservando como JSON")
                with self.engine.connect() as conn:
                    trans = conn.begin()
                    try:
                        # Adiciona coluna de contagem
                        add_count_sql = text(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN {column_name}_count INT DEFAULT 0
                        """)
                        conn.execute(add_count_sql)
                        
                        # Atualiza contagens
                        for idx, row in df.iterrows():
                            try:
                                if isinstance(row[column_name], str):
                                    data = json.loads(row[column_name])
                                else:
                                    data = row[column_name]
                                
                                count = len(data) if isinstance(data, list) else 1
                                update_sql = text(f"""
                                    UPDATE {table_name}
                                    SET {column_name}_count = {count}
                                    WHERE id = {row['id']}
                                """)
                                conn.execute(update_sql)
                            except:
                                pass
                        
                        trans.commit()
                        print(f"      ✅ Coluna {column_name}_count adicionada com contagens")
                        return 1
                    
                    except Exception as e:
                        trans.rollback()
                        raise e
            
            # Se é objeto, desagrupa os campos
            elif isinstance(sample_value, dict):
                print(f"      Objeto detectado - desagrupando campos")
                
                # Coleta todas as chaves possíveis
                all_keys = set()
                for value in df[column_name]:
                    if pd.notna(value):
                        try:
                            if isinstance(value, str):
                                data = json.loads(value)
                            else:
                                data = value
                            
                            if isinstance(data, dict):
                                all_keys.update(data.keys())
                        except:
                            pass
                
                if not all_keys:
                    print(f"      ⚠️ Nenhuma chave encontrada")
                    return 0
                
                print(f"      Chaves encontradas: {all_keys}")
                
                # Cria novas colunas para cada chave
                new_columns = {}
                for key in all_keys:
                    new_col_name = f"{column_name}_{key}"
                    new_columns[new_col_name] = []
                    
                    for value in df[column_name]:
                        if pd.notna(value):
                            try:
                                if isinstance(value, str):
                                    data = json.loads(value)
                                else:
                                    data = value
                                
                                if isinstance(data, dict):
                                    new_columns[new_col_name].append(data.get(key))
                            except:
                                new_columns[new_col_name].append(None)
                        else:
                            new_columns[new_col_name].append(None)
                
                # Atualiza a tabela
                with self.engine.connect() as conn:
                    trans = conn.begin()
                    
                    try:
                        # Remove coluna original
                        drop_col_sql = text(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                        conn.execute(drop_col_sql)
                        print(f"      ✓ Coluna original removida")
                        
                        # Adiciona novas colunas
                        for new_col_name in new_columns.keys():
                            add_col_sql = text(f"""
                                ALTER TABLE {table_name} 
                                ADD COLUMN {new_col_name} LONGTEXT
                            """)
                            conn.execute(add_col_sql)
                        
                        print(f"      ✓ {len(new_columns)} novas colunas adicionadas")
                        
                        # Atualiza dados
                        for idx, row in df.iterrows():
                            set_parts = []
                            for col_name, values in new_columns.items():
                                value = values[idx]
                                quoted = self._quote_value(value)
                                set_parts.append(f"{col_name} = {quoted}")
                            
                            set_clause = ", ".join(set_parts)
                            update_sql = text(f"""
                                UPDATE {table_name}
                                SET {set_clause}
                                WHERE id = {row['id']}
                            """)
                            conn.execute(update_sql)
                        
                        trans.commit()
                        print(f"      ✅ {len(df)} linhas atualizadas")
                        return len(new_columns)
                    
                    except Exception as e:
                        trans.rollback()
                        raise e
            
            else:
                print(f"      ⚠️ Tipo de dados não reconhecido")
                return 0
        
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return 0
    
    def _quote_value(self, value):
        """Escapa valor para SQL."""
        if value is None or pd.isna(value):
            return "NULL"
        if isinstance(value, str):
            escaped = value.replace("'", "\\'")
            return f"'{escaped}'"
        return str(value)


def main():
    """Função principal."""
    try:
        print("\n" + "="*70)
        print("🔄 DESAGRUPADOR DE COLUNAS JSON (MESMA TABELA)")
        print("="*70)
        print("\nEste script desagrupa colunas JSON mantendo os dados NA MESMA TABELA")
        print("Exemplo: paymentTerm JSON → paymentTerm_id, paymentTerm_description\n")
        
        app_config = ApplicationConfig()
        app = JSONMySQLApplication(app_config)
        flattener = InPlaceFlattener(DatabaseManager.get_engine())
        
        # Define as colunas a desagrupar
        denormalizations = [
            ('parcelas_contareceber_datacompetparcelas', 'paymentTerm'),
            ('parcelas_contareceber_datacompetparcelas', 'receipts'),
            ('parcelas_contareceber_datacompetparcelas', 'receiptsCategories'),
            ('parcelas_contareceber_datapagtoparcelas', 'paymentTerm'),
            ('parcelas_contareceber_datapagtoparcelas', 'receipts'),
            ('parcelas_contareceber_datapagtoparcelas', 'receiptsCategories'),
        ]
        
        print("Desagrupamentos a fazer:")
        for table, col in denormalizations:
            print(f"  - {table}.{col}")
        
        print("\n" + "-"*70)
        response = input("Deseja continuar? (s/n): ").strip().lower()
        
        if response != 's':
            print("Operação cancelada.")
            return
        
        total_cols_added = 0
        
        for table_name, column_name in denormalizations:
            print(f"\n{'='*70}")
            print(f"Processando: {table_name}")
            print(f"{'='*70}")
            
            cols_added = flattener.flatten_column_in_place(table_name, column_name)
            total_cols_added += cols_added
        
        print("\n" + "="*70)
        print("✨ Desagrupamento concluído!")
        print(f"   Total de colunas adicionadas: {total_cols_added}")
        print("="*70)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
