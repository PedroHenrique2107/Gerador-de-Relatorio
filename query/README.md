# Query - Execução da Query Padrão

## Função
Executa query SQL que consolida dados de 4 tabelas do Sienge e armazena resultado em `RELATORIO_CONSOLIDADO`.

## Setup
```bash
pip install -r requirements.txt
```

## Uso
```bash
python execute_query.py
```

## Query Padrão
A query está hardcoded em `execute_query.py` e consolida:
- SI_EXTRATO_CLIENTE_HISTORICO
- SI_DATACOMPETPARCELAS
- SI_DATAPAGTO_receipts
- SI_DATAPAGTO_receiptsCategories

## Tabela Resultante
`RELATORIO_CONSOLIDADO` - sempre contém dados da última execução (TRUNCATE antes de inserir).

## Manutenção
Para alterar a query, edite a constante `QUERY_PADRAO` em `execute_query.py`.
