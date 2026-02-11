#!/usr/bin/env python
"""
Script para DELETAR as tabelas extras criadas pela migração anterior.
"""

import sys
import os
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

logger = setup_logger('cleanup')


def delete_extra_tables():
    """Deleta todas as tabelas extras criadas."""
    
    app_config = ApplicationConfig()
    app = JSONMySQLApplication(app_config)
    engine = DatabaseManager.get_engine()
    
    # Lista de tabelas a deletar
    tables_to_delete = [
        'parcelas_contareceber_datacompetparcelas_paymentterm',
        'parcelas_contareceber_datacompetparcelas_receipts',
        'parcelas_contareceber_datacompetparcelas_receiptscategories',
        'parcelas_contareceber_datapagtoparcelas_paymentterm',
        'parcelas_contareceber_datapagtoparcelas_receipts',
        'parcelas_contareceber_datapagtoparcelas_receiptscategories',
    ]
    
    print("\n" + "="*70)
    print("🗑️ DELETANDO TABELAS EXTRAS")
    print("="*70)
    
    print("\nTabelas a deletar:")
    for table in tables_to_delete:
        print(f"  - {table}")
    
    print("\n" + "-"*70)
    response = input("Deseja continuar com a deleção? (s/n): ").strip().lower()
    
    if response != 's':
        print("Operação cancelada.")
        return
    
    with engine.connect() as conn:
        for table in tables_to_delete:
            try:
                # Verifica se tabela existe
                check_sql = text(f"SELECT 1 FROM information_schema.TABLES WHERE TABLE_NAME = '{table}'")
                result = conn.execute(check_sql).fetchone()
                
                if result:
                    # Deleta a tabela
                    drop_sql = text(f"DROP TABLE {table}")
                    conn.execute(drop_sql)
                    print(f"✅ Tabela deletada: {table}")
                else:
                    print(f"⏭️ Tabela não existe: {table}")
            
            except Exception as e:
                print(f"❌ Erro ao deletar {table}: {e}")
        
        conn.commit()
    
    print("\n" + "="*70)
    print("✨ Limpeza concluída!")
    print("="*70)


if __name__ == '__main__':
    try:
        delete_extra_tables()
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
