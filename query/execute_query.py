#!/usr/bin/env python3
"""Execute Query Padrao - Consolida dados do Sienge."""

import os
import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
API_ENV = ROOT_DIR / "api-server" / ".env"


def _load_envs() -> None:
    if BACKEND_ENV.exists():
        load_dotenv(BACKEND_ENV, override=True)
    if API_ENV.exists():
        load_dotenv(API_ENV, override=False)


def _required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise ValueError(f"{name} nao configurado")
    return value


_load_envs()

MYSQL_CONFIG = {
    "host": _required_env("MYSQL_HOST"),
    "port": int((os.getenv("MYSQL_PORT") or "3306").strip()),
    "user": _required_env("MYSQL_USER"),
    "password": _required_env("MYSQL_PASSWORD"),
    "database": _required_env("MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


QUERY_PADRAO = """
SELECT DISTINCT
  ech.companyId AS Codigoempresa,
  ech.companyName AS NomeDaEmpresa,
  CAST(sd.costCenterId AS CHAR) AS CodigoDoCentroDeCusto,
  sd.costCenterName AS NomeDoCentroDeCusto,
  CONCAT(
    SUBSTRING(sd.financialCategoryId, 1, 1), '.',
    SUBSTRING(sd.financialCategoryId, 2, 2), '.',
    SUBSTRING(sd.financialCategoryId, 4, 2), '.',
    SUBSTRING(sd.financialCategoryId, 6, 2)
  ) AS CodigoDoPlanoFinanceiroComMascara,
  sd.financialCategoryId AS numPlanoFinanceiro,
  sd.financialCategoryName AS PlanoFinanceiro,
  ech.customerId AS CodigoDoCliente,
  ech.customerName AS NomeDoCliente,
  ech.customerDocument AS NumeroCPFCNPJ,
  sd.documentNumber AS NumeroDoDocumento,
  sd.documentIdentificationName AS NomeDoDocumento,
  ech.billReceivableId AS NumeroDoTitulo,
  ech.Id AS NumeroDaParcela,
  ech.paymentTermsDescrition AS NomeDoTipoDeCondicao,
  DATE(ech.lastRenegotiationDate) AS DataDeEmissao,
  DATE(ech.dueDate) AS DataDeVencimento,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.originalValue, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS ValorOriginalRateado,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.originalValue, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2) -
    ROUND(COALESCE(ech.receiptValue, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS SaldoAtual,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.receiptValue, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS ValorDaBaixaRateado,
  DATE(ech.receiptDate) AS Datadabaixa,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.receiptExtra, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS AcrescimoRateado,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.receiptDiscount, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS DescontoRateado,
  REPLACE(REPLACE(REPLACE(FORMAT(
    ROUND(COALESCE(ech.receiptValue, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2) +
    ROUND(COALESCE(ech.receiptExtra, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2) -
    ROUND(COALESCE(ech.receiptDiscount, 0) * COALESCE(sd.financialCategoryRate, 0) / 100, 2), 2
  ), ',', '#'), '.', ','), '#', '.') AS ValorLiquido,
  sdr.accountNumber AS numConta,
  IF (
    UPPER(TRIM(sdr.accountNumber)) = 'REAPROFIN',
    'Distrato',
    IF (COALESCE(ech.receiptValue,0) = 0, 'A Receber',
        IF (ech.originalValue > ech.receiptValue,'Pagamento Parcial',
            IF (ech.originalValue = ech.receiptValue,'Pagamento Total', '')
        )
    )
  ) AS StatusParcela
FROM SI_EXTRATO_CLIENTE_HISTORICO ech
LEFT JOIN SI_DATACOMPETPARCELAS sd
  ON sd.companyId = ech.companyId
  AND sd.billId = ech.billReceivableId
  AND sd.installmentId = ech.Id
LEFT JOIN SI_DATAPAGTO_receipts sdr
  ON sdr.billId = ech.billReceivableId
  AND sdr.companyId = ech.companyId
  AND sdr.installmentId = ech.Id
  AND sdr.netAmount = ech.receiptValue
WHERE sd.financialCategoryId IS NOT NULL
"""


QUERY_COLUMNS = [
    "Codigoempresa",
    "NomeDaEmpresa",
    "CodigoDoCentroDeCusto",
    "NomeDoCentroDeCusto",
    "CodigoDoPlanoFinanceiroComMascara",
    "numPlanoFinanceiro",
    "PlanoFinanceiro",
    "CodigoDoCliente",
    "NomeDoCliente",
    "NumeroCPFCNPJ",
    "NumeroDoDocumento",
    "NomeDoDocumento",
    "NumeroDoTitulo",
    "NumeroDaParcela",
    "NomeDoTipoDeCondicao",
    "DataDeEmissao",
    "DataDeVencimento",
    "ValorOriginalRateado",
    "SaldoAtual",
    "ValorDaBaixaRateado",
    "Datadabaixa",
    "AcrescimoRateado",
    "DescontoRateado",
    "ValorLiquido",
    "numConta",
    "StatusParcela",
]


DDL_RELATORIO_EXATO = """
CREATE TABLE IF NOT EXISTS RELATORIO_CONSOLIDADO (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Codigoempresa BIGINT,
    NomeDaEmpresa VARCHAR(255),
    CodigoDoCentroDeCusto VARCHAR(100),
    NomeDoCentroDeCusto VARCHAR(255),
    CodigoDoPlanoFinanceiroComMascara VARCHAR(30),
    numPlanoFinanceiro VARCHAR(100),
    PlanoFinanceiro VARCHAR(255),
    CodigoDoCliente BIGINT,
    NomeDoCliente VARCHAR(255),
    NumeroCPFCNPJ VARCHAR(50),
    NumeroDoDocumento VARCHAR(80),
    NomeDoDocumento VARCHAR(255),
    NumeroDoTitulo BIGINT,
    NumeroDaParcela BIGINT,
    NomeDoTipoDeCondicao VARCHAR(120),
    DataDeEmissao DATE NULL,
    DataDeVencimento DATE NULL,
    ValorOriginalRateado VARCHAR(30),
    SaldoAtual VARCHAR(30),
    ValorDaBaixaRateado VARCHAR(30),
    Datadabaixa DATE NULL,
    AcrescimoRateado VARCHAR(30),
    DescontoRateado VARCHAR(30),
    ValorLiquido VARCHAR(30),
    numConta VARCHAR(50),
    StatusParcela VARCHAR(30),
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_data_execucao (data_execucao),
    INDEX idx_titulo (NumeroDoTitulo),
    INDEX idx_cliente (CodigoDoCliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def criar_tabela_consolidada(cursor) -> None:
    # Garante schema e ordem de colunas exatamente iguais ao padrao exigido.
    cursor.execute("DROP TABLE IF EXISTS RELATORIO_CONSOLIDADO")
    cursor.execute(DDL_RELATORIO_EXATO)
    print("Tabela RELATORIO_CONSOLIDADO recriada no padrao da QUERY_PADRAO", file=sys.stderr)


def _index_exists(cursor, table_name: str, index_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        LIMIT 1
        """,
        (table_name, index_name),
    )
    return cursor.fetchone() is not None


def garantir_indices_fonte(cursor) -> None:
    """Cria índices de join quando ausentes para acelerar a etapa 2."""
    idx_defs = [
        (
            "SI_EXTRATO_CLIENTE_HISTORICO",
            "idx_ech_join",
            "CREATE INDEX idx_ech_join ON SI_EXTRATO_CLIENTE_HISTORICO (companyId, billReceivableId, Id)",
        ),
        (
            "SI_DATACOMPETPARCELAS",
            "idx_sd_join",
            "CREATE INDEX idx_sd_join ON SI_DATACOMPETPARCELAS (companyId, billId, installmentId)",
        ),
        (
            "SI_DATAPAGTO_receipts",
            "idx_sdr_join",
            "CREATE INDEX idx_sdr_join ON SI_DATAPAGTO_receipts (companyId, billId, installmentId, netAmount)",
        ),
    ]

    for table_name, index_name, ddl in idx_defs:
        if _index_exists(cursor, table_name, index_name):
            continue
        print(f"Criando indice {index_name} em {table_name}...", file=sys.stderr)
        cursor.execute(ddl)
        print(f"Indice criado: {index_name}", file=sys.stderr)


def limpar_dados_antigos(cursor) -> None:
    cursor.execute("TRUNCATE TABLE RELATORIO_CONSOLIDADO")
    print("Tabela RELATORIO_CONSOLIDADO limpa", file=sys.stderr)


def executar_query_e_inserir(cursor) -> int:
    print("Executando query consolidada...", file=sys.stderr)
    columns_csv = ", ".join(QUERY_COLUMNS)
    insert_query = f"""
    INSERT INTO RELATORIO_CONSOLIDADO ({columns_csv})
    SELECT {columns_csv}
    FROM ({QUERY_PADRAO}) q
    """
    cursor.execute(insert_query)
    rows_inserted = cursor.rowcount
    print(f"Query executada: {rows_inserted} registros inseridos", file=sys.stderr)
    return rows_inserted


def main() -> int:
    print("=" * 60, file=sys.stderr)
    print("EXECUTANDO QUERY PADRAO - CONSOLIDACAO DE DADOS", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)

    connection = None
    try:
        print(
            f"Conectando em {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}...",
            file=sys.stderr,
        )
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()

        print("Conectado ao MySQL", file=sys.stderr)
        print(file=sys.stderr)

        garantir_indices_fonte(cursor)
        criar_tabela_consolidada(cursor)
        limpar_dados_antigos(cursor)
        rows = executar_query_e_inserir(cursor)
        connection.commit()

        print(file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"SUCESSO: {rows} registros consolidados", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        return 0
    except Exception as exc:
        print(f"\nERRO: {exc}", file=sys.stderr)
        if connection:
            connection.rollback()
        return 1
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    sys.exit(main())
