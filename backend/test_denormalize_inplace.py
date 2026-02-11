"""
Teste de denormalização IN-PLACE (sem MySQL).

Valida que a expansão das parcelas funciona corretamente
antes de sobrescrever a tabela no banco.
"""

import sys
from pathlib import Path

# Adiciona diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.denormalize_inplace import denormalize_extrato_inplace

def test_denormalize():
    """Testa a denormalização in-place."""
    
    json_file = Path("data/ExtratoClienteHistorico.json")
    
    if not json_file.exists():
        print(f"Arquivo não encontrado: {json_file}")
        return
    
    print("\n" + "="*70)
    print("TESTE - DENORMALIZACAO IN-PLACE")
    print("="*70)
    
    try:
        # Desnormaliza
        df = denormalize_extrato_inplace(json_file)
        
        print(f"\nOK: DENORMALIZACAO CONCLUIDA!")
        print(f"\nRESULTADO:")
        print(f"  Linhas originais: (documentos com parcelas agrupadas)")
        print(f"  Linhas após desnormalização: {len(df):,}")
        print(f"  (cada parcela como linha separada)")
        
        # Mostra amostra
        print(f"\nAMOSTRA - Primeiras 5 linhas:")
        cols = ['billReceivableId', 'customerName', 'installmentNumber', 'originalValue', 'dueDate']
        if not df.empty:
            print(df[cols].head(5).to_string(index=False))
        
        # Valida estrutura
        print(f"\nVALIDACOES:")
        print(f"  Colunas do DataFrame: {len(df.columns)}")
        print(f"  Coluna 'billReceivableId': {'OK' if 'billReceivableId' in df.columns else 'ERRO'}")
        print(f"  Coluna 'installmentNumber': {'OK' if 'installmentNumber' in df.columns else 'ERRO'}")
        print(f"  Coluna 'customerName': {'OK' if 'customerName' in df.columns else 'ERRO'}")
        print(f"  Coluna 'originalValue': {'OK' if 'originalValue' in df.columns else 'ERRO'}")
        
        # Estatísticas
        print(f"\nESTATISTICAS:")
        print(f"  Documentos únicos: {df['billReceivableId'].nunique():,}")
        print(f"  Total de linhas: {len(df):,}")
        print(f"  Parcelas por documento: {len(df) / df['billReceivableId'].nunique():.1f}")
        
        print(f"\nPROXIMO PASSO:")
        print(f"  Quando MySQL estiver acessível:")
        print(f"  $ python scripts/denormalize_inplace.py")
        print(f"\n  Isso vai SOBRESCREVER a tabela ExtratoClienteHistorico")
        print(f"  com os dados expandidos ({len(df):,} linhas)")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_denormalize()
