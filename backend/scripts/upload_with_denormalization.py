#!/usr/bin/env python
"""
Script interativo para upload de JSON com denormalization completa.

Cria múltiplas tabelas relacionadas para dados aninhados.
Implementa rastreamento e evita reuploads.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

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
from app.utils.complete_flattener import denormalize_json_file

logger = setup_logger('denorm_upload')
DATA_DIR = Path(__file__).parent.parent / 'data'


def list_json_files():
    """Lista todos os arquivos JSON disponíveis."""
    json_files = sorted(DATA_DIR.glob('*.json'))
    return json_files


def print_menu(files):
    """Exibe menu de seleção."""
    print("\n" + "="*70)
    print("📂 ARQUIVOS DISPONÍVEIS PARA UPLOAD (COM DENORMALIZAÇÃO COMPLETA)")
    print("="*70)
    
    for i, file in enumerate(files, 1):
        size_kb = file.stat().st_size / 1024
        print(f"{i}. {file.name:<45} ({size_kb:.1f} KB)")
    
    print("\n" + "-"*70)
    print("Opções: Digite os números dos arquivos separados por vírgula")
    print("Exemplo: 1,2 (para arquivos 1 e 2)")
    print("         1   (para arquivo 1)")
    print("         a   (para TODOS os arquivos)")
    print("         s   (para SAIR)")
    print("-"*70)


def get_user_selection(files):
    """Obtém seleção do usuário."""
    while True:
        print_menu(files)
        choice = input("\n👉 Sua escolha: ").strip().lower()
        
        if choice == 's':
            print("Operação cancelada.")
            return []
        
        if choice == 'a':
            return files
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected = [files[i] for i in indices if 0 <= i < len(files)]
            
            if not selected:
                print("❌ Seleção inválida! Tente novamente.")
                continue
            
            return selected
        
        except (ValueError, IndexError):
            print("❌ Seleção inválida! Tente novamente.")
            continue


def confirm_upload(files):
    """Confirma upload antes de executar."""
    print("\n" + "="*70)
    print("✅ ARQUIVOS SELECIONADOS PARA UPLOAD (COM DENORMALIZAÇÃO):")
    print("="*70)
    
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.name}")
    
    print("\n" + "-"*70)
    print("⚠️ AVISO: Cada arquivo pode gerar MÚLTIPLAS TABELAS relacionadas:")
    print("  - Tabela principal com dados achatados")
    print("  - Tabelas secundárias para arrays aninhados (receipts, financialCategories, etc)")
    print("-"*70)
    response = input("Deseja continuar com o upload? (s/n): ").strip().lower()
    
    return response == 's'


def upload_files(files):
    """Faz upload dos arquivos com denormalização completa."""
    app_config = ApplicationConfig(loader_mode='quick')
    app = JSONMySQLApplication(app_config)
    tracker = UploadTracker(DatabaseManager.get_engine())
    
    print("\n" + "="*70)
    print("🚀 INICIANDO UPLOAD COM DENORMALIZAÇÃO COMPLETA")
    print("="*70)
    
    results = []
    
    for i, file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processando: {file.name}")
        
        # Verifica se arquivo já foi feito upload
        existing_upload = tracker.file_already_uploaded(file)
        
        if existing_upload:
            print(f"⚠️ Arquivo JÁ FOI FEITO UPLOAD")
            print(f"   📌 Tabela: {existing_upload['table_name']}")
            print(f"   📊 Linhas inseridas: {existing_upload['rows_inserted']}")
            print(f"   📅 Data: {existing_upload['upload_date']}")
            print(f"   🔐 Hash: {existing_upload['file_hash']}")
            results.append({
                'file': file.name, 
                'status': 'skipped', 
                'reason': 'Arquivo duplicado',
                'existing_table': existing_upload['table_name']
            })
            continue
        
        try:
            print(f"   📊 Denormalizando estrutura...")
            start_time = datetime.now()
            
            # Denormaliza o arquivo em múltiplas tabelas
            main_df, related_dfs = denormalize_json_file(file, file.stem.lower())
            
            exec_time = (datetime.now() - start_time).total_seconds()
            
            print(f"   ✓ Estrutura denormalizada em {exec_time:.2f}s")
            print(f"   📋 Tabelas a criar: {len(related_dfs) + 1}")
            print(f"      - Tabela principal: {file.stem.lower()}")
            for table_name in related_dfs.keys():
                print(f"      - Tabela relacionada: {table_name}")
            
            # Carrega tabela principal
            main_table_name = file.stem.lower()
            print(f"\n   [1] Carregando tabela principal: {main_table_name}")
            print(f"       {len(main_df)} linhas, {len(main_df.columns)} colunas")
            
            # Converte para arquivo temporário
            temp_file = file.parent / f".{file.stem}_main_denorm.json"
            main_df.to_json(temp_file, orient='records', force_ascii=False)
            
            result_main = app.load_json(temp_file, main_table_name)
            total_rows = result_main.rows_inserted if result_main.success else 0
            
            if result_main.success:
                print(f"   ✅ Tabela principal: {result_main.rows_inserted} linhas inseridas")
                
                # Registra no rastreador
                tracker.register_upload(
                    file, 
                    main_table_name, 
                    result_main.rows_inserted,
                    exec_time,
                    status='success'
                )
                
                # Carrega tabelas relacionadas
                for table_idx, (rel_table_name, rel_df) in enumerate(related_dfs.items(), 2):
                    print(f"\n   [{table_idx}] Carregando tabela relacionada: {rel_table_name}")
                    print(f"       {len(rel_df)} linhas, {len(rel_df.columns)} colunas")
                    
                    temp_rel_file = file.parent / f".{file.stem}_{rel_table_name}_denorm.json"
                    rel_df.to_json(temp_rel_file, orient='records', force_ascii=False)
                    
                    result_rel = app.load_json(temp_rel_file, rel_table_name)
                    if result_rel.success:
                        print(f"   ✅ {rel_table_name}: {result_rel.rows_inserted} linhas inseridas")
                        total_rows += result_rel.rows_inserted
                    else:
                        print(f"   ⚠️ {rel_table_name}: Erro ao carregar")
                    
                    # Limpa arquivo temporário
                    try:
                        temp_rel_file.unlink()
                    except:
                        pass
                
                # Limpa arquivo principal
                try:
                    temp_file.unlink()
                except:
                    pass
                
                results.append({
                    'file': file.name, 
                    'status': 'success', 
                    'rows': total_rows,
                    'tables': len(related_dfs) + 1,
                    'main_table': main_table_name
                })
            
            else:
                error_msg = ", ".join(result_main.errors) if result_main.errors else "Erro desconhecido"
                print(f"   ⚠️ Erro na tabela principal: {error_msg}")
                
                tracker.register_upload(
                    file,
                    main_table_name,
                    0,
                    exec_time,
                    status='error',
                    error_message=error_msg
                )
                
                results.append({
                    'file': file.name, 
                    'status': 'error', 
                    'error': error_msg
                })
        
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
            results.append({
                'file': file.name, 
                'status': 'error', 
                'error': str(e)
            })
    
    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DO UPLOAD COM DENORMALIZAÇÃO")
    print("="*70)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    skipped_items = [r for r in results if r['status'] == 'skipped']
    
    total_rows = sum(r.get('rows', 0) for r in successful)
    total_tables = sum(r.get('tables', 0) for r in successful)
    
    if successful:
        print(f"\n✅ Arquivos com sucesso: {len(successful)}")
        for r in successful:
            print(f"   - {r['file']}: {r['rows']} linhas em {r['tables']} tabelas")
    
    if skipped_items:
        print(f"\n⏭️ Arquivos pulados (já existentes): {len(skipped_items)}")
        for r in skipped_items:
            print(f"   - {r['file']} (tabela: {r['existing_table']})")
    
    if failed:
        print(f"\n❌ Arquivos com erro: {len(failed)}")
        for r in failed:
            print(f"   - {r['file']}: {r['error']}")
    
    print(f"\n📈 Total de linhas inseridas: {total_rows}")
    print(f"📋 Total de tabelas criadas: {total_tables}")
    print(f"⏭️ Total de arquivos pulados: {len(skipped_items)}")
    print("="*70)


def main():
    """Função principal."""
    try:
        files = list_json_files()
        
        if not files:
            print("❌ Nenhum arquivo JSON encontrado em 'data/'")
            sys.exit(1)
        
        print("\n🎯 BEM-VINDO AO UPLOAD COM DENORMALIZAÇÃO COMPLETA")
        print("="*70)
        print("Este sistema achata todos os campos aninhados em colunas separadas")
        print("e cria tabelas relacionadas para arrays.")
        print("="*70)
        
        selected = get_user_selection(files)
        
        if not selected:
            sys.exit(0)
        
        if not confirm_upload(selected):
            print("Operação cancelada.")
            sys.exit(0)
        
        upload_files(selected)
        
        print("\n✨ Processo concluído!")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
