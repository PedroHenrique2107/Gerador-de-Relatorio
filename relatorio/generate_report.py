#!/usr/bin/env python3
"""
<<<<<<< HEAD
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
=======
Gerador de Relatório Consolidado (RELATORIO_CONSOLIDADO)

O que este script faz:
- Conecta no MySQL usando variáveis de ambiente (.env do backend e do api-server).
- Busca todos os registros da tabela/VIEW RELATORIO_CONSOLIDADO.
- Gera um arquivo de exportação no formato escolhido: CSV, XLSX (xls/xlsx) ou TXT.
- Imprime em STDOUT um JSON com metadados do arquivo (nome, tamanho, quantidade de linhas).

Uso (exemplos):
  python3 generate_report.py --formato csv  --output-dir ./downloads
  python3 generate_report.py --formato xlsx --output-dir ./downloads
  python3 generate_report.py --formato txt  --output-dir ./downloads

Observações importantes:
- Este script é chamado pelo Node (pythonRunner.runReportGeneration) e precisa imprimir um JSON válido em STDOUT.
- Logs de andamento/erro vão para STDERR para não “sujar” o JSON de saída.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv

>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
from generators.csv_generator import CSVGenerator
from generators.xls_generator import XLSGenerator
from generators.txt_generator import TXTGenerator

<<<<<<< HEAD
# Carregar .env do backend
backend_path = Path(__file__).parent.parent / 'backend'
env_path = backend_path / '.env'
load_dotenv(env_path)

# Carregar .env do api-server (para credenciais MySQL)
api_server_path = Path(__file__).parent.parent / 'api-server'
api_env_path = api_server_path / '.env'
load_dotenv(api_env_path)

# Configuração MySQL
=======
# =============================================================================
# Carregamento de configurações (.env)
# =============================================================================
# 1) Carrega .env do backend (fonte principal de variáveis, ex: MYSQL_*)
backend_path = Path(__file__).parent.parent / 'backend'
load_dotenv(backend_path / '.env')

# 2) Carrega .env do api-server (complementar) e sobrescreve se existir
api_server_path = Path(__file__).parent.parent / 'api-server'
load_dotenv(api_server_path / '.env')

# Configuração de conexão MySQL (lida do ambiente).
# Se alguma variável obrigatória estiver vazia, a conexão pode falhar.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
<<<<<<< HEAD
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
=======
    'cursorclass': pymysql.cursors.DictCursor,  # retorna cada linha como dict {coluna: valor}
}

# Mapeia formato -> classe geradora.
# Nota: "xls" e "xlsx" apontam para XLSGenerator, porém o arquivo gerado sai como XLSX.
GENERATORS = {
    'csv': CSVGenerator,
    'xls': XLSGenerator,
    'xlsx': XLSGenerator,
    'txt': TXTGenerator,
}


# =============================================================================
# Camada de dados (MySQL)
# =============================================================================
def buscar_dados_consolidados(cursor):
    """
    Busca os dados do relatório consolidado.

    Importante:
    - Usa SELECT explícito de colunas para manter estabilidade no layout do relatório.
    - Ordena por Titulo, ParcelaSequencial para facilitar leitura e conferência.
    """
    query = """
    SELECT
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
        Titulo, ParcelaSequencial, ParcelaCondicao, Codigoempresa, Empresa,
        Codcentro_de_custo, Centro_de_custo, Codcliente, Cliente, Documento,
        DocumentoProcessado, numdocumento, Origem, Tipocondicao, DataEmissao, DataVencimento,
        numPlanoFinanceiro, PlanoFinanceiro, Datadabaixa, Valororiginal,
        ValorPendente, Valordabaixa, Acrescimo, Desconto, ValorLiquido, numConta
    FROM RELATORIO_CONSOLIDADO
    ORDER BY Titulo, ParcelaSequencial
    """
<<<<<<< HEAD
    
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

=======
    cursor.execute(query)
    return cursor.fetchall()


# =============================================================================
# Utilitários (formato / nome / tamanho)
# =============================================================================
def normalizar_formato_excel(formato):
    """
    Normaliza o formato para a extensão real do arquivo.

    Regra:
    - Se o usuário pedir 'xls' ou 'xlsx', geramos 'xlsx' (gerador é o mesmo).
    - Qualquer outro formato passa direto.
    """
    return 'xlsx' if formato in ('xls', 'xlsx') else formato


def gerar_nome_arquivo(formato, record_count):
    """
    Gera nome de arquivo com timestamp e quantidade de registros.

    Exemplo:
      relatorio_20260211_120324_19618.xlsx
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extensao = normalizar_formato_excel(formato)
    return f'relatorio_{timestamp}_{record_count}.{extensao}'


def obter_tamanho_arquivo(filepath):
    """
    Retorna tamanho do arquivo em texto humano (B, KB, MB).
    """
    size_bytes = os.path.getsize(filepath)
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'


# =============================================================================
# Ponto de entrada (CLI)
# =============================================================================
def main():
    """
    Fluxo principal:
    1) Lê argumentos (--formato e --output-dir).
    2) Conecta no MySQL e busca dados consolidados.
    3) Gera arquivo no formato solicitado.
    4) Imprime JSON final em STDOUT (para o Node consumir).
    """
    parser = argparse.ArgumentParser(description='Gera relatorio consolidado')
    parser.add_argument('--formato', required=True, choices=['csv', 'xls', 'xlsx', 'txt'])
    parser.add_argument('--output-dir', required=True, help='Diretorio de saida')
    args = parser.parse_args()

    connection = None
    try:
        # Conecta no banco
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()

        # Log em STDERR para não atrapalhar o JSON (STDOUT)
        print('Buscando dados consolidados...', file=sys.stderr)

        # Busca dados
        rows = buscar_dados_consolidados(cursor)
        record_count = len(rows)
        if record_count == 0:
            # Falha controlada: não gera arquivo vazio
            raise ValueError('Nenhum dado encontrado em RELATORIO_CONSOLIDADO')

        # Prepara caminho de saída
        formato = normalizar_formato_excel(args.formato)
        filename = gerar_nome_arquivo(formato, record_count)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename

        # Instancia gerador correto e gera o arquivo
        generator_class = GENERATORS[formato]
        generator = generator_class()

        print(f'Gerando arquivo {formato.upper()}...', file=sys.stderr)
        generator.generate(rows, filepath)

        # Retorno para o Node: JSON puro em STDOUT
        result = {
            'fileName': filename,
            'fileSize': obter_tamanho_arquivo(filepath),
            'recordCount': record_count,
            'formato': formato,
        }
        print(json.dumps(result))

        # Log final (apenas informativo)
        print(f'Arquivo gerado: {filepath}', file=sys.stderr)
        return 0

    except Exception as e:
        # Erro vai em STDERR; o Node interpreta exit code != 0 como falha
        print(f'ERRO: {e}', file=sys.stderr)
        return 1

    finally:
        # Fecha conexão mesmo em caso de erro
        if connection:
            connection.close()


>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
if __name__ == '__main__':
    sys.exit(main())
