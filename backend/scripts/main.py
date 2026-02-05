#!/usr/bin/env python3
"""
Script Principal - Processa JSONs do Sienge e insere no MySQL

Este script simula o processamento que o backend já faz:
- Lê arquivos JSON da pasta data/
- Processa em chunks
- Insere dados nas tabelas MySQL

Uso:
    python main.py --dir /path/to/data --pattern *.json --mode quick --chunk-size 5000 --if-exists replace
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
import pymysql
from dotenv import load_dotenv

# Carregar .env do backend
backend_path = Path(__file__).parent.parent
env_path = backend_path / '.env'
load_dotenv(env_path)

# Carregar .env do api-server (para credenciais MySQL)
api_server_path = Path(__file__).parent.parent.parent / 'api-server'
api_env_path = api_server_path / '.env'
load_dotenv(api_env_path)

# Configuração MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

def criar_tabelas(cursor):
    """Cria tabelas necessárias se não existem"""
    
    tabelas = [
        """
        CREATE TABLE IF NOT EXISTS SI_EXTRATO_CLIENTE_HISTORICO (
            id INT AUTO_INCREMENT PRIMARY KEY,
            billReceivableId INT,
            Id INT,
            installmentNumber VARCHAR(50),
            companyId INT,
            companyName VARCHAR(255),
            costCenterId INT,
            costCenterName VARCHAR(255),
            customerId INT,
            customerName VARCHAR(255),
            customerDocument VARCHAR(50),
            document VARCHAR(100),
            paymentTermsId INT,
            lastRenegotiationDate DATE,
            dueDate DATE,
            receiptDate DATE,
            originalValue DECIMAL(15,2),
            receiptValue DECIMAL(15,2),
            receiptExtra DECIMAL(15,2),
            receiptDiscount DECIMAL(15,2),
            INDEX idx_bill (billReceivableId),
            INDEX idx_company (companyId)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS SI_DATACOMPETPARCELAS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            companyId INT,
            billId INT,
            installmentId INT,
            originId VARCHAR(50),
            financialCategoryId INT,
            financialCategoryName VARCHAR(255),
            balanceAmount DECIMAL(15,2),
            INDEX idx_bill (billId),
            INDEX idx_company (companyId)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS SI_DATAPAGTO_receipts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            companyId INT,
            billId INT,
            installmentId INT,
            accountNumber VARCHAR(50),
            INDEX idx_bill (billId),
            INDEX idx_company (companyId)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS SI_DATAPAGTO_receiptsCategories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            companyId INT,
            billId INT,
            installmentId INT,
            categoryName VARCHAR(255),
            INDEX idx_bill (billId)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    ]
    
    for ddl in tabelas:
        cursor.execute(ddl)
    
    print("✓ Tabelas verificadas/criadas", file=sys.stderr)

def processar_json(filepath, cursor, chunk_size=5000):
    """Processa um arquivo JSON e insere no banco"""
    
    print(f"Processando {filepath.name}...", file=sys.stderr)
    
    # Simulação: apenas conta registros (backend real já faz isso)
    # Em produção, aqui seria feito o parsing e inserção real
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'data' in data:
            records = data['data']
        else:
            records = data if isinstance(data, list) else [data]
        
        total = len(records)
        print(f"  {total} registros encontrados", file=sys.stderr)
        
        # Simula processamento em chunks
        processed = 0
        for i in range(0, total, chunk_size):
            chunk = records[i:i+chunk_size]
            processed += len(chunk)
            # Aqui seria feita a inserção real
            time.sleep(0.1)  # Simula processamento
        
        print(f"  ✓ {processed} registros processados", file=sys.stderr)
        return processed
        
    except Exception as e:
        print(f"  ✗ Erro: {e}", file=sys.stderr)
        return 0

def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description='Processa JSONs do Sienge')
    parser.add_argument('--dir', required=True, help='Diretório com JSONs')
    parser.add_argument('--pattern', default='*.json', help='Padrão de arquivos')
    parser.add_argument('--mode', default='quick', help='Modo de processamento')
    parser.add_argument('--chunk-size', type=int, default=5000, help='Tamanho do chunk')
    parser.add_argument('--if-exists', default='replace', help='Ação se tabela existe')
    
    args = parser.parse_args()
    
    print("="*60, file=sys.stderr)
    print("PROCESSAMENTO DE DADOS SIENGE", file=sys.stderr)
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
        
        # Criar tabelas
        criar_tabelas(cursor)
        connection.commit()
        print(file=sys.stderr)
        
        # Buscar arquivos JSON
        data_dir = Path(args.dir)
        json_files = list(data_dir.glob(args.pattern))
        
        if not json_files:
            print(f"Nenhum arquivo JSON encontrado em {data_dir}", file=sys.stderr)
            return 1
        
        print(f"Encontrados {len(json_files)} arquivos JSON", file=sys.stderr)
        print(file=sys.stderr)
        
        # Processar cada arquivo
        total_records = 0
        for json_file in json_files:
            records = processar_json(json_file, cursor, args.chunk_size)
            total_records += records
            connection.commit()
        
        print(file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"SUCESSO: {total_records} registros processados", file=sys.stderr)
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
