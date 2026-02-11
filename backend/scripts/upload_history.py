#!/usr/bin/env python
"""
Script para visualizar histórico e gerenciar uploads rastreados.

Mostra quais arquivos já foram feitos upload, quando, quantas linhas, etc.
"""

import sys
import os
from pathlib import Path

# ⚠️ VALIDA VIRTUAL ENVIRONMENT
if 'VIRTUAL_ENV' not in os.environ and not hasattr(sys, 'real_prefix') and sys.prefix == sys.base_prefix:
    error_msg = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌ ERRO: VIRTUAL ENVIRONMENT NÃO ATIVADO               ║
╚════════════════════════════════════════════════════════════════════════════╝

Execute primeiro:
   Windows: .venv\\Scripts\\activate
   macOS/Linux: source .venv/bin/activate
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application import JSONMySQLApplication, ApplicationConfig
from app.core import setup_logger, DatabaseManager
from app.utils.upload_tracker import UploadTracker

logger = setup_logger('upload_history')


def show_menu():
    """Exibe menu de opções."""
    print("\n" + "="*70)
    print("📋 GERENCIADOR DE HISTÓRICO DE UPLOADS")
    print("="*70)
    print("1. Ver histórico de uploads (últimos 20)")
    print("2. Ver detalhes de um arquivo específico")
    print("3. Voltar")
    print("-"*70)


def show_upload_history(tracker):
    """Mostra histórico de uploads."""
    history = tracker.get_upload_history(limit=20)
    
    if not history:
        print("\n📭 Nenhum upload registrado ainda.")
        return
    
    print("\n" + "="*70)
    print("📜 HISTÓRICO DE UPLOADS (últimos 20)")
    print("="*70)
    
    for i, upload in enumerate(history, 1):
        status_icon = "✅" if upload['status'] == 'success' else "❌"
        print(f"\n{i}. {status_icon} {upload['file_name']}")
        print(f"   Tabela: {upload['table_name']}")
        print(f"   Linhas: {upload['rows_inserted']}")
        print(f"   Data: {upload['upload_date']}")
        print(f"   Status: {upload['status']}")
    
    print("\n" + "="*70)


def check_file_duplicate(tracker):
    """Verifica se um arquivo já foi feito upload."""
    data_dir = Path(__file__).parent.parent / 'data'
    
    print("\n" + "="*70)
    print("🔍 VERIFICAR ARQUIVO DUPLICADO")
    print("="*70)
    
    # Lista arquivos
    json_files = sorted(data_dir.glob('*.json'))
    
    print("\nArquivos disponíveis:")
    for i, file in enumerate(json_files, 1):
        print(f"{i}. {file.name}")
    
    try:
        choice = int(input("\nEscolha um arquivo (número): ")) - 1
        if 0 <= choice < len(json_files):
            file = json_files[choice]
            result = tracker.file_already_uploaded(file)
            
            if result:
                print(f"\n✅ ARQUIVO JÁ FOI FEITO UPLOAD")
                print(f"   Hash: {result['file_hash']}")
                print(f"   Tabela: {result['table_name']}")
                print(f"   Linhas: {result['rows_inserted']}")
                print(f"   Data: {result['upload_date']}")
            else:
                print(f"\n⭕ Arquivo NÃO foi feito upload ainda")
                print(f"   Arquivo: {file.name}")
        else:
            print("❌ Opção inválida")
    
    except ValueError:
        print("❌ Digite um número válido")


def main():
    """Função principal."""
    try:
        app_config = ApplicationConfig()
        app = JSONMySQLApplication(app_config)
        tracker = UploadTracker(DatabaseManager.get_engine())
        
        while True:
            show_menu()
            choice = input("\n👉 Sua escolha: ").strip()
            
            if choice == '1':
                show_upload_history(tracker)
            
            elif choice == '2':
                check_file_duplicate(tracker)
            
            elif choice == '3':
                print("\nAté logo! 👋")
                break
            
            else:
                print("❌ Opção inválida!")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário.")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
