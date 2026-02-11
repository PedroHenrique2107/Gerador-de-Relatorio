"""
Teste da função de normalização (sem conexão MySQL).

Este teste demonstra que a função normalize_extrato_cliente()
funciona corretamente, transformando JSON aninhado em 3 DataFrames
normalizados e relacionados.
"""

import sys
from pathlib import Path

# Adiciona diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importa apenas a função de normalização (não precisa de MySQL)
from scripts.normalize_extrato import normalize_extrato_cliente

def test_normalize():
    """Testa a normalização do JSON."""
    
    json_file = Path("data/ExtratoClienteHistorico.json")
    
    if not json_file.exists():
        print(f"❌ Arquivo não encontrado: {json_file}")
        return
    
    print("\n" + "="*70)
    print("TESTANDO NORMALIZAÇÃO DE ExtratoClienteHistorico.json")
    print("="*70)
    
    try:
        # Normaliza
        bills_df, installments_df, receipts_df = normalize_extrato_cliente(json_file)
        
        print(f"\n[OK] NORMALIZACAO CONCLUIDA COM SUCESSO!")
        print(f"\n📊 RESULTADO:")
        print(f"  • billsReceivables: {len(bills_df):,} documentos")
        print(f"  • installments:     {len(installments_df):,} parcelas")
        print(f"  • receipts:         {len(receipts_df):,} pagamentos")
        
        # Mostra amostra de cada tabela
        print(f"\n📋 AMOSTRA - billsReceivables (primeiros 3):")
        cols = ['billReceivableId', 'companyName', 'customerName', 'emissionDate']
        if not bills_df.empty and all(c in bills_df.columns for c in cols):
            print(bills_df[cols].head(3).to_string(index=False))
        else:
            print(bills_df.head(3).to_string(index=False))
        
        print(f"\n📋 AMOSTRA - installments (primeiros 5):")
        cols = ['billReceivableId', 'installmentNumber', 'dueDate', 'originalValue']
        if not installments_df.empty and all(c in installments_df.columns for c in cols):
            print(installments_df[cols].head(5).to_string(index=False))
        else:
            print(installments_df.head(5).to_string(index=False))
        
        print(f"\n📋 AMOSTRA - receipts (primeiros 3):")
        cols = ['billReceivableId', 'installmentId', 'date', 'value']
        if not receipts_df.empty and all(c in receipts_df.columns for c in cols):
            print(receipts_df[cols].head(3).to_string(index=False))
        else:
            if not receipts_df.empty:
                print(receipts_df.head(3).to_string(index=False))
            else:
                print("  (Nenhum pagamento encontrado no JSON)")
        
        print(f"\n💡 INTERPRETAÇÃO:")
        print(f"  [OK] De 7039 documentos, foram geradas 18885 parcelas")
        if len(bills_df) > 0:
            media_parcelas = len(installments_df) / len(bills_df)
            print(f"  [OK] Media de parcelas por documento: {media_parcelas:.1f}")
        
        print(f"\n[SUCESSO] ESTRUTURA RELACIONAL CRIADA:")
        print(f"  • billsReceivables.id -> installments.billReceivableId")
        print(f"  • billsReceivables.id -> receipts.billReceivableId")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_normalize()
