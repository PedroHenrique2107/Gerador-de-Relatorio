#!/usr/bin/env python3
"""
Gerador de RelatÃ³rio Consolidado (RELATORIO_CONSOLIDADO)

O que este script faz:
- Conecta no MySQL usando variÃ¡veis de ambiente (.env do backend e do api-server).
- Busca todos os registros da tabela/VIEW RELATORIO_CONSOLIDADO.
- Gera um arquivo de exportaÃ§Ã£o no formato escolhido: CSV, XLSX (xls/xlsx) ou TXT.
- Imprime em STDOUT um JSON com metadados do arquivo (nome, tamanho, quantidade de linhas).

Uso (exemplos):
  python3 generate_report.py --formato csv  --output-dir ./downloads
  python3 generate_report.py --formato xlsx --output-dir ./downloads
  python3 generate_report.py --formato txt  --output-dir ./downloads

ObservaÃ§Ãµes importantes:
- Este script são chamado pelo Node (pythonRunner.runReportGeneration) e precisa imprimir um JSON vÃ¡lido em STDOUT.
- Logs de andamento/erro vÃ£o para STDERR para nÃ£o â€œsujarâ€ o JSON de saÃ­da.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv

from generators.csv_generator import CSVGenerator
from generators.xls_generator import XLSGenerator
from generators.txt_generator import TXTGenerator

# =============================================================================
# Carregamento de configuraÃ§Ãµes (.env)
# =============================================================================
# 1) Carrega .env do backend (fonte principal de variÃ¡veis, ex: MYSQL_*)
backend_path = Path(__file__).parent.parent / 'backend'
load_dotenv(backend_path / '.env')

# 2) Carrega .env do api-server (complementar) e sobrescreve se existir
api_server_path = Path(__file__).parent.parent / 'api-server'
load_dotenv(api_server_path / '.env')

# ConfiguraÃ§Ã£o de conexÃ£o MySQL (lida do ambiente).
# Se alguma variÃ¡vel obrigatÃ³ria estiver vazia, a conexÃ£o pode falhar.
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,  # retorna cada linha como dict {coluna: valor}
}

# Mapeia formato -> classe geradora.
# Nota: "xls" e "xlsx" apontam para XLSGenerator, porÃ©m o arquivo gerado sai como XLSX.
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
    Busca os dados do relatÃ³rio consolidado.

    Importante:
    - Usa SELECT explÃ­cito de colunas para manter estabilidade no layout do relatÃ³rio.
    - Ordena por Titulo, ParcelaSequencial para facilitar leitura e conferÃªncia.
    """
    query = """
    SELECT
        Codigoempresa,
        NomeDaEmpresa,
        CodigoDoCentroDeCusto,
        NomeDoCentroDeCusto,
        CodigoDoPlanoFinanceiroComMascara,
        numPlanoFinanceiro,
        PlanoFinanceiro,
        CodigoDoCliente,
        NomeDoCliente,
        NumeroCPFCNPJ,
        NumeroDoDocumento,
        NomeDoDocumento,
        NumeroDoTitulo,
        NumeroDaParcela,
        NomeDoTipoDeCondicao,
        DataDeEmissao,
        DataDeVencimento,
        ValorOriginalRateado,
        SaldoAtual,
        ValorDaBaixaRateado,
        Datadabaixa,
        AcrescimoRateado,
        DescontoRateado,
        ValorLiquido,
        numConta,
        StatusParcela
    FROM RELATORIO_CONSOLIDADO
    ORDER BY NumeroDoTitulo, NumeroDaParcela
    """
    cursor.execute(query)
    return cursor.fetchall()


# =============================================================================
# UtilitÃ¡rios (formato / nome / tamanho)
# =============================================================================
def normalizar_formato_excel(formato):
    """
    Normaliza o formato para a extensÃ£o real do arquivo.

    Regra:
    - Se o usuÃ¡rio pedir 'xls' ou 'xlsx', geramos 'xlsx' (gerador Ã© o mesmo).
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
    1) LÃª argumentos (--formato e --output-dir).
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
            # Falha controlada: nÃ£o gera arquivo vazio
            raise ValueError('Nenhum dado encontrado em RELATORIO_CONSOLIDADO')

        # Prepara caminho de saÃ­da
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
        # Fecha conexÃ£o mesmo em caso de erro
        if connection:
            connection.close()


if __name__ == '__main__':
    sys.exit(main())
