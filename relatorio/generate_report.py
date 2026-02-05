#!/usr/bin/env python3
"""
Gerador de Relatórios - Exporta RELATORIO_CONSOLIDADO

Este script:
1. Conecta no MySQL
2. Lê dados de RELATORIO_CONSOLIDADO (última execução)
3. Gera arquivo no formato solicitado (CSV, XLS, TXT)
4. Salva em pasta de downloads
5. Retorna JSON com metadados do arquivo

Uso:
    python generate_report.py --formato csv --output-dir /caminho/downloads
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import pymysql
from dotenv import load_dotenv

# Importa geradores
from generators.csv_generator import CSVGenerator
from generators.xls_generator import XLSGenerator
from generators.txt_generator import TXTGenerator

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

# Mapeamento de geradores
GENERATORS = {
    'csv': CSVGenerator,
    'xls': XLSGenerator,
    'txt': TXTGenerator
}

def buscar_dados_consolidados(cursor):
    """Busca dados da tabela RELATORIO_CONSOLIDADO"""
    
    query = """
    SELECT 
        Titulo, ParcelaSequencial, ParcelaCondicao, Codigoempresa, Empresa,
        Codcentro_de_custo, Centro_de_custo, Codcliente, Cliente, Documento,
        DocumentoProcessado, numdocumento, Origem, Tipocondicao, DataEmissao, DataVencimento,
        numPlanoFinanceiro, PlanoFinanceiro, Datadabaixa, Valororiginal,
        ValorPendente, Valordabaixa, Acrescimo, Desconto, ValorLiquido, numConta
    FROM RELATORIO_CONSOLIDADO
    ORDER BY Titulo, ParcelaSequencial
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    return rows

def gerar_nome_arquivo(formato, record_count):
    """Gera nome do arquivo com timestamp e contagem"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extensao = formato.lower()
    
    return f"relatorio_{timestamp}_{record_count}.{extensao}"

def obter_tamanho_arquivo(filepath):
    """Retorna tamanho do arquivo formatado"""
    
    size_bytes = os.path.getsize(filepath)
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description='Gera relatório consolidado')
    parser.add_argument('--formato', required=True, choices=['csv', 'xls', 'txt'])
    parser.add_argument('--output-dir', required=True, help='Diretório de saída')
    
    args = parser.parse_args()
    
    connection = None
    try:
        # Conectar MySQL
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Buscar dados
        print("Buscando dados consolidados...", file=sys.stderr)
        rows = buscar_dados_consolidados(cursor)
        record_count = len(rows)
        
        if record_count == 0:
            raise ValueError("Nenhum dado encontrado em RELATORIO_CONSOLIDADO")
        
        print(f"✓ {record_count} registros encontrados", file=sys.stderr)
        
        # Gerar nome do arquivo
        filename = gerar_nome_arquivo(args.formato, record_count)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        
        # Selecionar gerador
        GeneratorClass = GENERATORS[args.formato]
        generator = GeneratorClass()
        
        # Gerar arquivo
        print(f"Gerando arquivo {args.formato.upper()}...", file=sys.stderr)
        generator.generate(rows, filepath)
        
        # Obter metadados
        file_size = obter_tamanho_arquivo(filepath)
        
        # Retornar resultado em JSON (para Node.js parsear)
        result = {
            'fileName': filename,
            'fileSize': file_size,
            'recordCount': record_count,
            'formato': args.formato
        }
        
        print(json.dumps(result))  # stdout para Node.js capturar
        
        print(f"✓ Arquivo gerado: {filepath}", file=sys.stderr)
        return 0
        
    except Exception as e:
        print(f"✗ ERRO: {e}", file=sys.stderr)
        return 1
        
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    sys.exit(main())
