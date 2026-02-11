"""
Inspeciona a estrutura do JSON ExtratoClienteHistorico.
"""

import json
from pathlib import Path

json_file = Path('data/ExtratoClienteHistorico.json')

with open(json_file, 'r', encoding='utf-8') as f:
    content = json.load(f)

data = content['data']
first = data[0]

print(f"Total de documentos: {len(data)}")
print(f"Primeira parcela tem {len(first['installments'])} parcelas")
print()

# Primeira parcela
first_inst = first['installments'][0]
print("Chaves da primeira parcela:")
for k in first_inst.keys():
    v = first_inst[k]
    if isinstance(v, list):
        print(f"  {k}: {type(v).__name__} (length={len(v)})")
    elif isinstance(v, dict):
        print(f"  {k}: {type(v).__name__} (keys={list(v.keys())})")
    else:
        print(f"  {k}: {v}")

print("\n\nSe tem receipts/pagamentos:")
if first_inst.get('receipts'):
    print(f"  Tem {len(first_inst['receipts'])} pagamentos")
    if first_inst['receipts']:
        print(f"  Chaves do primeiro pagamento:")
        for k in first_inst['receipts'][0].keys():
            print(f"    {k}: {first_inst['receipts'][0][k]}")
else:
    print("  Não tem receipts/pagamentos")
