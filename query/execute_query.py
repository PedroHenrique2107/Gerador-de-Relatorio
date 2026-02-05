#!/usr/bin/env python3
"""
Execute Query Padrão - Consolida dados do Sienge

Este script:
1. Conecta no MySQL
2. Executa a query padrão que consolida 4 tabelas
3. Cria tabela temporária RELATORIO_CONSOLIDADO
4. Insere resultado da query nesta tabela
5. Adiciona timestamp de execução

Uso:
    python execute_query.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pymysql
from dotenv import load_dotenv

# Carregar .env do backend
backend_path = Path(__file__).parent.parent / 'backend'
env_path = backend_path / '.env'
load_dotenv(env_path)

# Carregar .env do api-server (para credenciais MySQL)
api_server_path = Path(__file__).parent.parent / 'api-server'
api_env_path = api_server_path / '.env'
load_dotenv(api_env_path)

# Configuração MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Query padrão (exatamente como fornecida)
QUERY_PADRAO = """
SELECT DISTINCT
  SI_EXTRATO_CLIENTE_HISTORICO.billReceivableId AS Titulo,
  SI_EXTRATO_CLIENTE_HISTORICO.Id AS ParcelaSequencial,
  SI_EXTRATO_CLIENTE_HISTORICO.installmentNumber AS ParcelaCondicao,
  SI_EXTRATO_CLIENTE_HISTORICO.companyId AS Codigoempresa,
  SI_EXTRATO_CLIENTE_HISTORICO.companyName AS Empresa,
  SI_EXTRATO_CLIENTE_HISTORICO.costCenterId AS Codcentro_de_custo,
  SI_EXTRATO_CLIENTE_HISTORICO.costCenterName AS Centro_de_custo,
  SI_EXTRATO_CLIENTE_HISTORICO.customerId AS Codcliente,
  SI_EXTRATO_CLIENTE_HISTORICO.customerName AS Cliente,
  SI_EXTRATO_CLIENTE_HISTORICO.customerDocument AS Documento,
  SUBSTRING_INDEX(
    SI_EXTRATO_CLIENTE_HISTORICO.document,
    '.',
    LENGTH(SI_EXTRATO_CLIENTE_HISTORICO.document) - LENGTH(REPLACE(SI_EXTRATO_CLIENTE_HISTORICO.document, '.', ''))
  ) AS DocumentoProcessado,
  SUBSTRING_INDEX(SI_EXTRATO_CLIENTE_HISTORICO.document, '.', -1) AS numdocumento,
  sd.originId AS Origem,
  SI_EXTRATO_CLIENTE_HISTORICO.paymentTermsId AS Tipocondicao,
  SI_EXTRATO_CLIENTE_HISTORICO.lastRenegotiationDate AS DataEmissao,
  SI_EXTRATO_CLIENTE_HISTORICO.dueDate AS DataVencimento,
  sd.financialCategoryId AS numPlanoFinanceiro,
  sd.financialCategoryName AS PlanoFinanceiro,
  SI_EXTRATO_CLIENTE_HISTORICO.receiptDate AS Datadabaixa,
  SI_EXTRATO_CLIENTE_HISTORICO.originalValue AS Valororiginal,
  sd.balanceAmount AS ValorPendente,
  SI_EXTRATO_CLIENTE_HISTORICO.receiptValue AS Valordabaixa,
  SI_EXTRATO_CLIENTE_HISTORICO.receiptExtra AS Acrescimo,
  SI_EXTRATO_CLIENTE_HISTORICO.receiptDiscount AS Desconto,
  (
    COALESCE(SI_EXTRATO_CLIENTE_HISTORICO.receiptValue, 0)
    + COALESCE(SI_EXTRATO_CLIENTE_HISTORICO.receiptExtra, 0)
    - COALESCE(SI_EXTRATO_CLIENTE_HISTORICO.receiptDiscount, 0)
  ) AS ValorLiquido,
  sdr.accountNumber AS numConta
FROM SI_EXTRATO_CLIENTE_HISTORICO
LEFT OUTER JOIN SI_DATACOMPETPARCELAS sd
  ON sd.companyId = SI_EXTRATO_CLIENTE_HISTORICO.companyId
 AND sd.billId = SI_EXTRATO_CLIENTE_HISTORICO.billReceivableId
 AND sd.installmentId = SI_EXTRATO_CLIENTE_HISTORICO.Id
LEFT OUTER JOIN SI_DATAPAGTO_receipts sdr
  ON SI_EXTRATO_CLIENTE_HISTORICO.billReceivableId = sdr.billId
 AND SI_EXTRATO_CLIENTE_HISTORICO.companyId = sdr.companyId
 AND SI_EXTRATO_CLIENTE_HISTORICO.Id = sdr.installmentId
LEFT JOIN SI_DATAPAGTO_receiptsCategories src
  ON src.companyId = sdr.companyId
 AND src.billId = sdr.billId
 AND src.installmentId = sdr.installmentId
WHERE sd.financialCategoryId IS NOT NULL
"""

def criar_tabela_consolidada(cursor):
    """Cria tabela RELATORIO_CONSOLIDADO se não existe"""
    
    ddl = """
    CREATE TABLE IF NOT EXISTS RELATORIO_CONSOLIDADO (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Titulo INT,
        ParcelaSequencial INT,
        ParcelaCondicao VARCHAR(50),
        Codigoempresa INT,
        Empresa VARCHAR(255),
        Codcentro_de_custo INT,
        Centro_de_custo VARCHAR(255),
        Codcliente INT,
        Cliente VARCHAR(255),
        Documento VARCHAR(50),
        DocumentoProcessado TEXT,
        numdocumento VARCHAR(50),
        Origem VARCHAR(50),
        Tipocondicao VARCHAR(50),
        DataEmissao DATE,
        DataVencimento DATE,
        numPlanoFinanceiro INT,
        PlanoFinanceiro VARCHAR(255),
        Datadabaixa DATE,
        Valororiginal DECIMAL(15,2),
        ValorPendente DECIMAL(15,2),
        Valordabaixa DECIMAL(15,2),
        Acrescimo DECIMAL(15,2),
        Desconto DECIMAL(15,2),
        ValorLiquido DECIMAL(15,2),
        numConta VARCHAR(50),
        data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_data_execucao (data_execucao),
        INDEX idx_titulo (Titulo),
        INDEX idx_cliente (Codcliente)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    cursor.execute(ddl)
    print("✓ Tabela RELATORIO_CONSOLIDADO verificada/criada", file=sys.stderr)

def limpar_dados_antigos(cursor):
    """Remove dados antigos para inserir novos (sempre pega última execução)"""
    
    cursor.execute("TRUNCATE TABLE RELATORIO_CONSOLIDADO")
    print("✓ Tabela RELATORIO_CONSOLIDADO limpa", file=sys.stderr)

def executar_query_e_inserir(cursor):
    """Executa query padrão e insere resultado em RELATORIO_CONSOLIDADO"""
    
    print("Executando query consolidada...", file=sys.stderr)
    
    # Insere resultado direto na tabela
    insert_query = f"""
    INSERT INTO RELATORIO_CONSOLIDADO (
        Titulo, ParcelaSequencial, ParcelaCondicao, Codigoempresa, Empresa,
        Codcentro_de_custo, Centro_de_custo, Codcliente, Cliente, Documento,
        DocumentoProcessado, numdocumento, Origem, Tipocondicao, DataEmissao, DataVencimento,
        numPlanoFinanceiro, PlanoFinanceiro, Datadabaixa, Valororiginal,
        ValorPendente, Valordabaixa, Acrescimo, Desconto, ValorLiquido, numConta
    )
    {QUERY_PADRAO}
    """
    
    cursor.execute(insert_query)
    rows_inserted = cursor.rowcount
    
    print(f"✓ Query executada: {rows_inserted} registros inseridos", file=sys.stderr)
    return rows_inserted

def main():
    """Função principal"""
    
    print("="*60, file=sys.stderr)
    print("EXECUTANDO QUERY PADRÃO - CONSOLIDAÇÃO DE DADOS", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(file=sys.stderr)
    
    connection = None
    try:
        # Conectar MySQL
        print(f"Conectando em {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}...", file=sys.stderr)
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print("✓ Conectado ao MySQL", file=sys.stderr)
        print(file=sys.stderr)
        
        # 1. Criar tabela se não existe
        criar_tabela_consolidada(cursor)
        
        # 2. Limpar dados antigos
        limpar_dados_antigos(cursor)
        
        # 3. Executar query e inserir
        rows = executar_query_e_inserir(cursor)
        
        # 4. Commit
        connection.commit()
        
        print(file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"SUCESSO: {rows} registros consolidados", file=sys.stderr)
        print("="*60, file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}", file=sys.stderr)
        if connection:
            connection.rollback()
        return 1
        
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    sys.exit(main())
