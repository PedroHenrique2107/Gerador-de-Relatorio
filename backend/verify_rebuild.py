import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
from dotenv import load_dotenv
from urllib.parse import quote_plus
import json
load_dotenv()

db_host = os.getenv('MYSQL_HOST', 'localhost')
db_port = os.getenv('MYSQL_PORT', '3306')
db_user = os.getenv('MYSQL_USER', 'dev_pricing')
db_pass = os.getenv('MYSQL_PASSWORD', 'Smart123!@#')
db_name = os.getenv('MYSQL_DATABASE', 'dev_pricing')

db_pass_encoded = quote_plus(db_pass)
database_url = f'mysql+pymysql://{db_user}:{db_pass_encoded}@{db_host}:{db_port}/{db_name}'

from app.core.database import DatabaseManager
from sqlalchemy import text, inspect

DatabaseManager.initialize(database_url)

engine = DatabaseManager.get_engine()
inspector = inspect(engine)

for table_name in ['parcelas_contareceber_datacompetparcelas', 'parcelas_contareceber_datapagtoparcelas']:
    cols = inspector.get_columns(table_name)
    col_names = [c['name'] for c in cols]
    print(f'\n{table_name}:')
    print(f'  Colunas totais: {len(cols)}')
    
    # Contar registros
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT COUNT(*) as cnt FROM `{table_name}`'))
        count = result.scalar()
        print(f'  Registros: {count}')
    
    # Mostrar algumas colunas importantes
    receipts_cols = [c for c in col_names if 'receipts_' in c and 'receiptsCategories' not in c]
    categories_cols = [c for c in col_names if 'receiptsCategories_' in c]
    
    print(f'  Colunas receipts expandidas: {len(receipts_cols)}')
    if receipts_cols:
        print(f'    Exemplos: {receipts_cols[:3]}')
    
    print(f'  Colunas receiptsCategories expandidas: {len(categories_cols)}')
    if categories_cols:
        print(f'    Exemplos: {categories_cols[:3]}')
    
    # Mostrar uma linha de amostra
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT paymentTerm_id, receipts_0_operationTypeId, receiptsCategories_0_costCenterId FROM `{table_name}` LIMIT 1'))
        row = result.fetchone()
        if row:
            print(f'  Amostra: paymentTerm_id={row[0]}, receipts_0_operationTypeId={row[1]}, receiptsCategories_0_costCenterId={row[2]}')

