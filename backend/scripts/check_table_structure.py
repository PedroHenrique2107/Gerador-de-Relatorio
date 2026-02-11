#!/usr/bin/env python
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.application import ApplicationConfig, JSONMySQLApplication
from app.core import DatabaseManager
from sqlalchemy import inspect, text

app_config = ApplicationConfig()
app = JSONMySQLApplication(app_config)
engine = DatabaseManager.get_engine()
inspector = inspect(engine)

# Mostra colunas da primeira tabela
table = 'parcelas_contareceber_datacompetparcelas'
cols = inspector.get_columns(table)
print(f"Colunas de {table} ({len(cols)} total):")
for c in cols:
    print(f"  {c['name']} - {c['type']}")

# Mostra primary key
pk = inspector.get_pk_constraint(table)
print(f"\nChave primária: {pk['constrained_columns']}")

# Mostra uma amostra dos dados
print("\nPrimeira linha:")
with engine.connect() as conn:
    result = conn.execute(text(f"SELECT * FROM {table} LIMIT 1")).fetchone()
    if result:
        print(f"Colunas no result: {len(result)}")

