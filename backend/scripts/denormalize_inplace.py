"""
Denormaliza ExtratoClienteHistorico IN-PLACE.

Carrega JSON aninhado e expande em uma única tabela ExtratoClienteHistorico
SEM criar tabelas adicionais. Cada parcela vira uma linha separada.

⚠️ ATENÇÃO: SOBRESCREVE a tabela original!
"""

import os
import sys
from pathlib import Path

# Validação de venv ANTES de qualquer import
if not hasattr(sys, 'real_prefix') and not (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
):
    print("\n" + "="*70)
    print("ERRO: Virtual environment NAO esta ativado!")
    print("="*70)
    print("\nAbra um terminal e execute:")
    print("  Windows:  .venv\\Scripts\\activate")
    print("  Linux:    source .venv/bin/activate")
    print("="*70 + "\n")
    sys.exit(1)

# Adiciona diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
import pandas as pd
import json
from sqlalchemy import text

from app.core import get_logger, DatabaseManager
from app.application import JSONMySQLApplication, ApplicationConfig

logger = get_logger(__name__)


def denormalize_extrato_inplace(json_file: Path) -> pd.DataFrame:
    """
    Desnormaliza JSON e expande em um único DataFrame.
    
    Carrega ExtratoClienteHistorico.json e expande as parcelas
    em linhas separadas, mantendo tudo em uma única tabela.
    
    Args:
        json_file: Caminho do arquivo JSON
    
    Returns:
        DataFrame: Dados expandidos prontos para inserir em ExtratoClienteHistorico
    
    Raises:
        FileNotFoundError: Se arquivo não existe
        ValueError: Se JSON inválido
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
    
    # Extrai array de dados
    if isinstance(content, dict) and 'data' in content:
        data = content['data']
    elif isinstance(content, list):
        data = content
    else:
        raise ValueError("JSON não tem estrutura esperada")
    
    if not data:
        raise ValueError("Arquivo JSON está vazio")
    
    logger.info(f"Carregado: {len(data)} documentos originais")
    
    # Estrutura para armazenar dados expandidos
    expanded_data = []
    
    # Processa cada documento
    for record in data:
        # Dados comuns do documento
        bill_id = record.get('billReceivableId')
        company = record.get('company', {})
        cost_center = record.get('costCenter', {})
        customer = record.get('customer', {})
        
        # Extrai parcelas
        installments = record.get('installments', [])
        
        if installments:
            # EXPANDE: Uma linha por parcela
            for inst in installments:
                row = {
                    # Dados do documento
                    'billReceivableId': bill_id,
                    'companyId': company.get('id'),
                    'companyName': company.get('name'),
                    'costCenterId': cost_center.get('id'),
                    'costCenterName': cost_center.get('name'),
                    'customerId': customer.get('id'),
                    'customerName': customer.get('name'),
                    'customerDocument': customer.get('document'),
                    'emissionDate': record.get('emissionDate'),
                    'document': record.get('document'),
                    'privateArea': record.get('privateArea'),
                    'oldestInstallmentDate': record.get('oldestInstallmentDate'),
                    'revokedBillReceivableDate': record.get('revokedBillReceivableDate'),
                    'lastRenegotiationDate': record.get('lastRenegotiationDate'),
                    'correctionDate': record.get('correctionDate'),
                    
                    # Dados da parcela (EXPANDIDOS)
                    'installmentId': inst.get('id'),
                    'installmentNumber': inst.get('installmentNumber'),
                    'baseDate': inst.get('baseDate'),
                    'dueDate': inst.get('dueDate'),
                    'originalValue': inst.get('originalValue'),
                    'currentBalance': inst.get('currentBalance'),
                    'currentBalanceWithAddition': inst.get('currentBalanceWithAddition'),
                    'installmentSituation': inst.get('installmentSituation'),
                    'generatedBillet': inst.get('generatedBillet'),
                    'annualCorrection': inst.get('annualCorrection'),
                    'sentToScripturalCharge': inst.get('sentToScripturalCharge'),
                    'indexerId': inst.get('indexerId'),
                    'paymentTermsId': inst.get('paymentTerms', {}).get('id'),
                    'paymentTermsDescription': inst.get('paymentTerms', {}).get('descrition'),
                    
                    # Dados dos pagamentos (primeiro pagamento, se houver)
                    'receipts': json.dumps(inst.get('receipts', [])),  # JSON como string
                }
                expanded_data.append(row)
        else:
            # Se não tem parcelas, insere mesmo assim com um registro
            row = {
                'billReceivableId': bill_id,
                'companyId': company.get('id'),
                'companyName': company.get('name'),
                'costCenterId': cost_center.get('id'),
                'costCenterName': cost_center.get('name'),
                'customerId': customer.get('id'),
                'customerName': customer.get('name'),
                'customerDocument': customer.get('document'),
                'emissionDate': record.get('emissionDate'),
                'document': record.get('document'),
                'privateArea': record.get('privateArea'),
                'oldestInstallmentDate': record.get('oldestInstallmentDate'),
                'revokedBillReceivableDate': record.get('revokedBillReceivableDate'),
                'lastRenegotiationDate': record.get('lastRenegotiationDate'),
                'correctionDate': record.get('correctionDate'),
                'installmentId': None,
                'installmentNumber': None,
                'baseDate': None,
                'dueDate': None,
                'originalValue': None,
                'currentBalance': None,
                'currentBalanceWithAddition': None,
                'installmentSituation': None,
                'generatedBillet': None,
                'annualCorrection': None,
                'sentToScripturalCharge': None,
                'indexerId': None,
                'paymentTermsId': None,
                'paymentTermsDescription': None,
                'receipts': None,
            }
            expanded_data.append(row)
    
    # Converte para DataFrame
    df = pd.DataFrame(expanded_data) if expanded_data else pd.DataFrame()
    
    logger.info(f"Desnormalização completa:")
    logger.info(f"  De {len(data)} documentos originais")
    logger.info(f"  Para {len(df)} linhas (com parcelas expandidas)")
    
    return df


def main():
    """
    Carrega, desnormaliza e SOBRESCREVE ExtratoClienteHistorico.
    """
    try:
        # Arquivo de entrada
        json_file = Path("data/ExtratoClienteHistorico.json")
        
        if not json_file.exists():
            logger.error(f"Arquivo não encontrado: {json_file}")
            return
        
        logger.info("\n" + "="*70)
        logger.info("DENORMALIZANDO ExtratoClienteHistorico.json (IN-PLACE)")
        logger.info("="*70)
        
        # Passo 1: Desnormaliza
        df = denormalize_extrato_inplace(json_file)
        
        # Passo 2: Inicializa aplicação
        logger.info("\nInicializando aplicacao...")
        app_config = ApplicationConfig(env="development", loader_mode="quick")
        app = JSONMySQLApplication(app_config)
        
        # Passo 3: Obtém engine
        engine = DatabaseManager.get_engine()
        
        # Passo 4: SOBRESCREVE tabela ExtratoClienteHistorico
        logger.info("\nSobrescrevendo tabela ExtratoClienteHistorico...")
        logger.warning("  ATENCAO: Deletando dados existentes...")
        
        with engine.connect() as conn:
            try:
                conn.execute(text("DROP TABLE IF EXISTS ExtratoClienteHistorico"))
                conn.commit()
                logger.info("  Tabela antiga removida")
            except Exception as e:
                logger.warning(f"  Nao foi possivel remover (pode nao existir): {e}")
        
        # Insere dados expandidos
        logger.info("\nInserindo dados expandidos...")
        
        if not df.empty:
            df.to_sql(
                'ExtratoClienteHistorico',
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=5000,
            )
            logger.info(f"  OK: {len(df)} linhas inseridas")
        
        # Passo 5: Exibe resumo
        logger.info("\n" + "="*70)
        logger.info("OK: DENORMALIZACAO CONCLUIDA COM SUCESSO!")
        logger.info("="*70)
        logger.info(f"\nRESULTADO:")
        logger.info(f"  Tabela ExtratoClienteHistorico atualizada")
        logger.info(f"  De: Documentos com parcelas agrupadas")
        logger.info(f"  Para: {len(df):,} linhas (parcelas expandidas)")
        logger.info(f"\nESTRUTURA:")
        logger.info(f"  Cada linha = 1 parcela de 1 documento")
        logger.info(f"  Campos de documento repetidos para cada parcela")
        logger.info(f"  Parcelas separadas (NAO agrupadas)")
        logger.info(f"\nNO DBFORGE:")
        logger.info(f"  ExtratoClienteHistorico tem {len(df):,} registros")
        logger.info(f"  Cada um é uma parcela visivel")
        logger.info(f"  Sem arrays colapsados")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"ERRO: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
