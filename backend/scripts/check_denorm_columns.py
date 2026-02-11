#!/usr/bin/env python
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.application import ApplicationConfig, JSONMySQLApplication
from app.core import DatabaseManager
from sqlalchemy import inspect

app_config = ApplicationConfig()
app = JSONMySQLApplication(app_config)
engine = DatabaseManager.get_engine()
inspector = inspect(engine)

table = 'parcelas_contareceber_datacompetparcelas'
cols = inspector.get_columns(table)
print(f"Procurando por colunas desagrupadas em {table}:")
found = False
for c in cols:
    if 'payment' in c['name'].lower() or 'receipt' in c['name'].lower():
        print(f"  ENCONTRADO: {c['name']}")
        found = True

if not found:
    print("  NENHUMA coluna encontrada!")
    print("\nTodas as colunas:")
    for c in cols:
        print(f"  - {c['name']}")
