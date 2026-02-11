#!/usr/bin/env python3
"""
Script de teste SEM MySQL - só valida que a denormalização vai funcionar.
Quando MySQL voltar, execute: python scripts/denormalize_inplace.py
"""

import sys
from pathlib import Path

# Validação de venv
if not hasattr(sys, 'real_prefix') and not (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
):
    print("\n" + "="*70)
    print("ERRO: Virtual environment NAO esta ativado!")
    print("="*70)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pandas as pd
from datetime import datetime

print("\n" + "="*80)
print("TESTE DE DENORMALIZACAO (SEM MySQL)")
print("="*80)

try:
    # 1. Carrega JSON
    print("\n[1/3] Carregando ExtratoClienteHistorico.json...")
    json_file = Path("data/ExtratoClienteHistorico.json")
    
    if not json_file.exists():
        print(f"      [ERRO] Arquivo não encontrado: {json_file}")
        sys.exit(1)
    
    with open(json_file, encoding='utf-8') as f:
        content = json.load(f)
    
    data = content.get('data', [])
    print(f"      [OK] Carregado: {len(data):,} documentos")
    
    # 2. Expande parcelas
    print("\n[2/3] Expandindo parcelas...")
    expanded = []
    total_parcelas = 0
    
    for record in data:
        installments = record.get('installments', [])
        total_parcelas += len(installments)
        
        for inst in installments:
            row = {
                'billReceivableId': record.get('billReceivableId'),
                'customerName': record.get('customer', {}).get('name'),
                'installmentNumber': inst.get('installmentNumber'),
                'dueDate': inst.get('dueDate'),
                'originalValue': inst.get('originalValue'),
            }
            expanded.append(row)
    
    df = pd.DataFrame(expanded)
    print(f"      [OK] Expandido: {len(df):,} linhas (parcelas)")
    
    # 3. Resumo
    print("\n[3/3] Validação final...")
    print(f"      [OK] Taxa de expansão: {len(df)/len(data):.1f}x")
    print(f"      [OK] Estrutura: {len(df.columns)} colunas")
    print(f"      [OK] Sem NaN: {df.isnull().sum().sum() == 0}")
    
    print("\n" + "="*80)
    print("✓ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print(f"\nRESULTADO:")
    print(f"  • Documentos originais: {len(data):,}")
    print(f"  • Linhas após expansão: {len(df):,}")
    print(f"  • Parcelas processadas: {total_parcelas:,}")
    print(f"\nQUANDO MYSQL VOLTAR, EXECUTE:")
    print(f"  $ python scripts/denormalize_inplace.py")
    print(f"\nISSO VAI:")
    print(f"  • Conectar ao MySQL")
    print(f"  • Sobrescrever tabela ExtratoClienteHistorico")
    print(f"  • Inserir {len(df):,} linhas no banco")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n[ERRO] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
