#!/usr/bin/env python
"""
Script interativo para selecionar e fazer upload de arquivos JSON.

Permite escolher quais arquivos JSON da pasta data/ fazer upload no banco.
Implementa sistema de rastreamento para evitar reuploads.
"""

import sys
import os
import json
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

logger = setup_logger('select_upload')
DATA_DIR = Path(__file__).parent.parent / 'data'


def normalize_json_file(file_path: Path) -> Path:
    """
    Normaliza arquivo JSON para formato esperado (array de objetos).
    Se o JSON é um dict com uma chave 'data', extrai o array.
    Converte objetos aninhados em JSON strings para armazenar como TEXT.
    
    Returns:
        Path ao arquivo temporário normalizado
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Se é um dict, tenta extrair a chave 'data'
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                data = data['data']
            else:
                # Se é um dict simples, converte para array
                data = [data]
        
        # Converte objetos e arrays aninhados em strings JSON (sem flatten estrutural)
        processed_data = []
        for item in data:
            processed_item = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    # Preserva como JSON string com indentação
                    processed_item[key] = json.dumps(value, ensure_ascii=False, indent=2)
                else:
                    processed_item[key] = value
            processed_data.append(processed_item)
        
        # Cria arquivo temporário normalizado
        temp_file = file_path.parent / f".{file_path.stem}_normalized.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, default=str)
        
        return temp_file
    
    except Exception as e:
        logger.error(f"Erro ao normalizar {file_path}: {e}")
        raise


def list_json_files():
    """Lista todos os arquivos JSON disponíveis."""
    json_files = sorted(DATA_DIR.glob('*.json'))
    return json_files


def print_menu(files):
    """Exibe menu de seleção."""
    print("\n" + "="*70)
    print("📂 ARQUIVOS DISPONÍVEIS PARA UPLOAD")
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
    print("✅ ARQUIVOS SELECIONADOS PARA UPLOAD:")
    print("="*70)
    
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.name}")
    
    print("\n" + "-"*70)
    response = input("Deseja continuar com o upload? (s/n): ").strip().lower()
    
    return response == 's'


def upload_files(files):
    """Faz upload dos arquivos selecionados com rastreamento."""
    app_config = ApplicationConfig(loader_mode='quick')
    app = JSONMySQLApplication(app_config)
    tracker = UploadTracker(DatabaseManager.get_engine())
    
    print("\n" + "="*70)
    print("🚀 INICIANDO UPLOAD COM VERIFICAÇÃO DE DUPLICATAS")
    print("="*70)
    
    results = []
    temp_files = []
    skipped = 0
    
    try:
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
                skipped += 1
                continue
            
            try:
                # Normaliza o JSON (SEM flatten)
                normalized_file = normalize_json_file(file)
                temp_files.append(normalized_file)
                
                # Deduz nome da tabela a partir do arquivo
                table_name = file.stem.lower()
                result = app.load_json(normalized_file, table_name)
                
                if result.success:
                    print(f"✅ Sucesso! {result.rows_inserted} linhas inseridas")
                    
                    # Registra no rastreador
                    tracker.register_upload(
                        file, 
                        table_name, 
                        result.rows_inserted,
                        result.execution_time,
                        status='success'
                    )
                    
                    results.append({
                        'file': file.name, 
                        'status': 'success', 
                        'rows': result.rows_inserted,
                        'table': table_name
                    })
                else:
                    error_msg = ", ".join(result.errors) if result.errors else "Erro desconhecido"
                    print(f"⚠️ Erro: {error_msg}")
                    
                    # Registra falha no rastreador
                    tracker.register_upload(
                        file,
                        table_name,
                        result.rows_inserted,
                        result.execution_time,
                        status='error',
                        error_message=error_msg
                    )
                    
                    results.append({
                        'file': file.name, 
                        'status': 'error', 
                        'error': error_msg
                    })
            
            except Exception as e:
                print(f"❌ Erro ao carregar: {e}")
                results.append({
                    'file': file.name, 
                    'status': 'error', 
                    'error': str(e)
                })
    
    finally:
        # Limpa arquivos temporários
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
    
    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DO UPLOAD")
    print("="*70)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    skipped_items = [r for r in results if r['status'] == 'skipped']
    
    total_rows = sum(r.get('rows', 0) for r in successful)
    
    if successful:
        print(f"\n✅ Arquivos com sucesso: {len(successful)}")
        for r in successful:
            print(f"   - {r['file']}: {r['rows']} linhas")
    
    if skipped_items:
        print(f"\n⏭️ Arquivos pulados (já existentes): {len(skipped_items)}")
        for r in skipped_items:
            print(f"   - {r['file']} (tabela: {r['existing_table']})")
    
    if failed:
        print(f"\n❌ Arquivos com erro: {len(failed)}")
        for r in failed:
            print(f"   - {r['file']}: {r['error']}")
    
    print(f"\n📈 Total de linhas inseridas: {total_rows}")
    print(f"⏭️ Total de arquivos pulados: {skipped}")
    print("="*70)


def main():
    """Função principal."""
    try:
        files = list_json_files()
        
        if not files:
            print("❌ Nenhum arquivo JSON encontrado em 'data/'")
            sys.exit(1)
        
        print("\n🎯 BEM-VINDO AO SELETOR DE UPLOAD JSON")
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
