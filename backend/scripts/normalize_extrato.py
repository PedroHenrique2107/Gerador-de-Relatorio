"""
Normaliza dados de ExtratoClienteHistorico em 3 tabelas relacionadas.

O JSON original tem estrutura aninhada:
{
  "codigoCliente": "1234",
  "nomeClienteEmpresa": "Empresa X",
  "installments": [
    {"numero_parcela": 1, "valor": 100.00},
    {"numero_parcela": 2, "valor": 100.00}
  ]
}

Após normalização, teremos 3 tabelas:
- billsReceivables: Cliente/Empresa/Documento
- installments: Cada parcela como linha separada (SOLUÇÃO PARA DBFORGE)
- receipts: Cada pagamento como linha separada
"""

import os
import sys
from pathlib import Path

# Validação de venv ANTES de qualquer import
if not hasattr(sys, 'real_prefix') and not (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
):
    print("\n" + "="*70)
    print("❌ ERRO: Virtual environment NÃO está ativado!")
    print("="*70)
    print("\nAbra um terminal e execute:")
    print("  • Windows:  .venv\\Scripts\\activate")
    print("  • Linux:    source .venv/bin/activate")
    print("  • macOS:    source .venv/bin/activate")
    print("\nDepois execute novamente este script.")
    print("="*70 + "\n")
    sys.exit(1)

# Adiciona diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Tuple
import pandas as pd
import json
from sqlalchemy import text

from app.core import get_logger, DatabaseManager
from app.application import JSONMySQLApplication, ApplicationConfig

logger = get_logger(__name__)


def drop_tables_if_exist(engine, table_names: list):
    """
    Remove tabelas se existirem (para começar do zero).
    
    Args:
        engine: SQLAlchemy engine
        table_names: Lista de nomes de tabelas
    """
    with engine.connect() as conn:
        for table_name in table_names:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
                logger.info(f"  ✓ Tabela {table_name} removida (se existia)")
            except Exception as e:
                logger.warning(f"  ⚠ Não foi possível remover {table_name}: {e}")


def create_foreign_keys(engine):
    """
    Cria relacionamentos entre tabelas com foreign keys.
    
    Args:
        engine: SQLAlchemy engine
    """
    try:
        with engine.connect() as conn:
            # FK: installments → billsReceivables
            try:
                conn.execute(text("""
                    ALTER TABLE installments 
                    ADD CONSTRAINT fk_installments_bills 
                    FOREIGN KEY (billReceivableId) 
                    REFERENCES billsReceivables(id)
                """))
                logger.info("  ✓ FK criada: installments → billsReceivables")
            except:
                pass  # Pode já existir
            
            # FK: receipts → billsReceivables
            try:
                conn.execute(text("""
                    ALTER TABLE receipts 
                    ADD CONSTRAINT fk_receipts_bills 
                    FOREIGN KEY (billReceivableId) 
                    REFERENCES billsReceivables(id)
                """))
                logger.info("  ✓ FK criada: receipts → billsReceivables")
            except:
                pass
            
            conn.commit()
    except Exception as e:
        logger.warning(f"⚠ Não foi possível criar foreign keys: {e}")


def normalize_extrato_cliente(json_file: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Denormaliza JSON de ExtratoClienteHistorico em 3 DataFrames relacionados.
    
    Transforma a estrutura aninhada em tabelas normalizadas com
    relacionamentos via foreign keys.
    
    Args:
        json_file: Caminho do arquivo JSON
    
    Returns:
        Tuple[DataFrame, DataFrame, DataFrame]: 
            - bills_df: Contas a receber (billReceivableId, company, customer)
            - installments_df: Parcelas (cada uma como linha separada!)
            - receipts_df: Pagamentos (cada um como linha separada!)
    
    Raises:
        FileNotFoundError: Se arquivo não existe
        ValueError: Se JSON inválido ou estrutura inesperada
    """
    json_file = Path(json_file)
    
    if not json_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {json_file}")
    
    logger.info(f"Carregando JSON: {json_file}")
    
    # Carrega JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}")
    
    # Extrai array de dados (pode estar em "data" ou ser direto)
    if isinstance(content, dict) and 'data' in content:
        data = content['data']
    elif isinstance(content, list):
        data = content
    else:
        raise ValueError("JSON não tem estrutura esperada (deve ter 'data' ou ser array direto)")
    
    if not data:
        raise ValueError("Arquivo JSON está vazio")
    
    logger.info(f"✓ Carregado: {len(data)} registros")
    
    # Estruturas para armazenar dados normalizados
    bills_data = []
    installments_data = []
    receipts_data = []
    
    receipt_id = 1  # ID sequencial para receipts
    
    # Processa cada bill/documento
    for record in data:
        # === TABELA: billsReceivables ===
        bill_record = {
            'billReceivableId': record.get('billReceivableId'),
            'companyId': record.get('company', {}).get('id'),
            'companyName': record.get('company', {}).get('name'),
            'costCenterId': record.get('costCenter', {}).get('id'),
            'costCenterName': record.get('costCenter', {}).get('name'),
            'customerId': record.get('customer', {}).get('id'),
            'customerName': record.get('customer', {}).get('name'),
            'customerDocument': record.get('customer', {}).get('document'),
            'emissionDate': record.get('emissionDate'),
            'document': record.get('document'),
            'privateArea': record.get('privateArea'),
            'oldestInstallmentDate': record.get('oldestInstallmentDate'),
            'revokedBillReceivableDate': record.get('revokedBillReceivableDate'),
        }
        bills_data.append(bill_record)
        
        # === TABELA: installments ===
        # AQUI É O IMPORTANTE: Cada parcela vira uma linha separada!
        installments = record.get('installments', [])
        
        if installments:
            for inst in installments:
                installment_record = {
                    'billReceivableId': record.get('billReceivableId'),
                    'installmentId': inst.get('id'),
                    'installmentNumber': inst.get('installmentNumber'),
                    'baseDate': inst.get('baseDate'),
                    'dueDate': inst.get('dueDate'),
                    'originalValue': inst.get('originalValue'),
                    'currentBalance': inst.get('currentBalance'),
                    'currentBalanceWithAddition': inst.get('currentBalanceWithAddition'),
                    'installmentSituation': inst.get('installmentSituation'),
                    'generatedBillet': inst.get('generatedBillet'),
                }
                installments_data.append(installment_record)
                
                # === TABELA: receipts ===
                # Cada pagamento como linha separada
                receipts = inst.get('receipts', [])
                
                if receipts:
                    for rec in receipts:
                        receipt_record = {
                            'receiptId': receipt_id,
                            'billReceivableId': record.get('billReceivableId'),
                            'installmentId': inst.get('id'),
                            'date': rec.get('date'),
                            'value': rec.get('value'),
                            'discount': rec.get('discount'),
                            'extra': rec.get('extra'),
                            'netReceipt': rec.get('netReceipt'),
                            'type': rec.get('type'),
                        }
                        receipts_data.append(receipt_record)
                        receipt_id += 1
    
    # Converte para DataFrames
    bills_df = pd.DataFrame(bills_data) if bills_data else pd.DataFrame()
    installments_df = pd.DataFrame(installments_data) if installments_data else pd.DataFrame()
    receipts_df = pd.DataFrame(receipts_data) if receipts_data else pd.DataFrame()
    
    logger.info(f"✓ Normalização completa:")
    logger.info(f"  • billsReceivables: {len(bills_df)} registros")
    logger.info(f"  • installments: {len(installments_df)} registros")
    logger.info(f"  • receipts: {len(receipts_df)} registros")
    
    return bills_df, installments_df, receipts_df


def main():
    """
    Carrega e normaliza ExtratoClienteHistorico.json.
    
    Passos:
    1. Carrega JSON
    2. Normaliza em 3 tabelas
    3. Insere em MySQL com a aplicação
    4. Exibe resumo
    """
    try:
        # Arquivo de entrada
        json_file = Path("data/ExtratoClienteHistorico.json")
        
        if not json_file.exists():
            logger.error(f"❌ Arquivo não encontrado: {json_file}")
            logger.info("Coloque ExtratoClienteHistorico.json em ./data/")
            return
        
        logger.info("\n" + "="*70)
        logger.info("NORMALIZANDO ExtratoClienteHistorico.json")
        logger.info("="*70)
        
        # Passo 1: Normaliza
        bills_df, installments_df, receipts_df = normalize_extrato_cliente(json_file)
        
        # Passo 2: Inicializa aplicação
        logger.info("\n📚 Inicializando aplicação...")
        app_config = ApplicationConfig(env="development", loader_mode="quick")
        app = JSONMySQLApplication(app_config)
        
        # Passo 3: Remove tabelas antigas se existirem
        logger.info("\n🧹 Limpando tabelas antigas...")
        engine = DatabaseManager.get_engine()
        drop_tables_if_exist(engine, ['installments', 'receipts', 'billsReceivables'])
        
        # Passo 4: Insere cada tabela
        logger.info("\n📥 Carregando dados em MySQL...")
        
        # billsReceivables
        if not bills_df.empty:
            logger.info("\n→ Carregando billsReceivables...")
            
            bills_df.to_sql(
                'billsReceivables',
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=5000,
            )
            logger.info(f"✓ billsReceivables: {len(bills_df)} linhas")
        
        # installments
        if not installments_df.empty:
            logger.info("\n→ Carregando installments...")
            
            installments_df.to_sql(
                'installments',
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=5000,
            )
            logger.info(f"✓ installments: {len(installments_df)} linhas ← CADA PARCELA COMO LINHA!")
        
        # receipts
        if not receipts_df.empty:
            logger.info("\n→ Carregando receipts...")
            
            receipts_df.to_sql(
                'receipts',
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=5000,
            )
            logger.info(f"✓ receipts: {len(receipts_df)} linhas ← CADA PAGAMENTO COMO LINHA!")
        
        # Passo 5: Cria relacionamentos
        logger.info("\n🔗 Criando relacionamentos (Foreign Keys)...")
        create_foreign_keys(engine)
        
        # Passo 6: Exibe resumo
        logger.info("\n" + "="*70)
        logger.info("✅ NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("="*70)
        logger.info(f"\n📊 RESULTADO:")
        logger.info(f"  • billsReceivables: {len(bills_df):,} documentos")
        logger.info(f"  • installments:     {len(installments_df):,} parcelas (VISÍVEIS NO DBFORGE)")
        logger.info(f"  • receipts:         {len(receipts_df):,} pagamentos")
        logger.info(f"\n🔗 RELACIONAMENTOS:")
        logger.info(f"  • installments → billsReceivables (billReceivableId)")
        logger.info(f"  • receipts → billsReceivables (billReceivableId)")
        logger.info(f"\n💡 NO DBFORGE, AGORA VOCÊ VÊ:")
        logger.info(f"  ✓ Cada parcela como UMA LINHA separada (não mais colapsada)")
        logger.info(f"  ✓ Cada pagamento como UMA LINHA separada")
        logger.info(f"  ✓ Todos os {len(bills_df):,} clientes com dados desnormalizados")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ ERRO: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
