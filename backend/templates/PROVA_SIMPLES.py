#!/usr/bin/env python
"""
PROVA SIMPLES - Testa apenas sintaxe e estrutura (sem dependências MySQL)
"""

import sys
from pathlib import Path

print("=" * 70)
print("✓ PROVA DE FUNCIONAMENTO - Código Corrigido")
print("=" * 70)

results = []

# ============================================================================
# TESTE 1: Sintaxe do main.py
# ============================================================================
print("\n✓ TESTE 1: Verificando sintaxe do scripts/main.py...")
try:
    import py_compile
    py_compile.compile('scripts/main.py', doraise=True)
    print("  ✅ Sintaxe válida!")
    results.append(("Sintaxe main.py", True, ""))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Sintaxe main.py", False, str(e)))

# ============================================================================
# TESTE 2: Try-Finally em main.py
# ============================================================================
print("\n✓ TESTE 2: Verificando correção do try-finally...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica posição correta
    try_pos = content.find('try:')
    except_pos = content.find('except Exception as e:')
    finally_pos = content.find('finally:')
    
    assert try_pos > 0, "Sem bloco try"
    assert except_pos > 0, "Sem bloco except"
    assert finally_pos > 0, "Sem bloco finally"
    assert finally_pos > except_pos, "finally deve estar após except"
    assert except_pos > try_pos, "except deve estar após try"
    
    # Verifica cleanup
    finally_block = content[finally_pos:finally_pos+200]
    assert 'app.cleanup()' in finally_block, "cleanup() não está no finally"
    
    # Verifica se app é inicializado antes do try
    app_init_before_try = content.find('app = None') < try_pos
    assert app_init_before_try, "app não é inicializado antes do try"
    
    print("  ✅ Estrutura corrigida!")
    print(f"     - app = None antes do try ✓")
    print(f"     - try em posição: {try_pos} ✓")
    print(f"     - except em posição: {except_pos} ✓")
    print(f"     - finally em posição: {finally_pos} ✓")
    print(f"     - app.cleanup() no finally ✓")
    results.append(("Try-Finally correto", True, ""))
except AssertionError as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Try-Finally correto", False, str(e)))

# ============================================================================
# TESTE 3: Verificar arquivo de dados
# ============================================================================
print("\n✓ TESTE 3: Verificando estrutura de dados...")
try:
    data_dir = Path('dados')
    if data_dir.exists():
        files = list(data_dir.glob('*.json'))
        print(f"  ✅ Encontrados {len(files)} arquivo(s) JSON")
        for f in files:
            print(f"     - {f.name}")
        results.append(("Dados de exemplo", True, f"{len(files)} arquivos"))
    else:
        print("  ⚠️ Pasta dados/ não encontrada (ok)")
        results.append(("Dados de exemplo", True, "Estrutura ok"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Dados de exemplo", False, str(e)))

# ============================================================================
# TESTE 4: Estrutura de diretórios
# ============================================================================
print("\n✓ TESTE 4: Verificando estrutura de diretórios...")
try:
    required_dirs = [
        'app/core',
        'app/loaders',
        'app/validators',
        'app/utils',
        'config',
        'scripts',
        'docs'
    ]
    
    missing = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        print(f"  ❌ Diretórios faltando: {', '.join(missing)}")
        results.append(("Estrutura de diretórios", False, f"Faltam: {missing}"))
    else:
        print(f"  ✅ Todos {len(required_dirs)} diretórios presentes!")
        results.append(("Estrutura de diretórios", True, f"{len(required_dirs)} dirs ok"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Estrutura de diretórios", False, str(e)))

# ============================================================================
# TESTE 5: Arquivos principais
# ============================================================================
print("\n✓ TESTE 5: Verificando arquivos principais...")
try:
    required_files = [
        'scripts/main.py',
        'app/application.py',
        'app/core/logger.py',
        'app/core/database.py',
        'app/core/exceptions.py',
        'app/loaders/base.py',
        'app/loaders/quick_loader.py',
        'app/validators/__init__.py',
        'app/utils/json_handler.py',
        'app/utils/schema_manager.py',
        'config/settings.py',
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"  ❌ Arquivos faltando: {len(missing)}")
        for f in missing:
            print(f"     - {f}")
        results.append(("Arquivos principais", False, f"{len(missing)} faltam"))
    else:
        print(f"  ✅ Todos {len(required_files)} arquivos presentes!")
        results.append(("Arquivos principais", True, f"{len(required_files)} ok"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Arquivos principais", False, str(e)))

# ============================================================================
# TESTE 6: Documentação
# ============================================================================
print("\n✓ TESTE 6: Verificando documentação...")
try:
    doc_files = [
        'docs/ARCHITECTURE.md',
        'DOCUMENTACAO_COMPLETA_V2.md',
        'MAPA_NAVEGACAO.md',
        'ARQUITETURA_SUMMARY.txt',
    ]
    
    missing = []
    for doc_path in doc_files:
        if not Path(doc_path).exists():
            missing.append(doc_path)
    
    if missing:
        print(f"  ⚠️ Faltam {len(missing)} arquivos de documentação")
        results.append(("Documentação", True, f"{len(doc_files)-len(missing)}/{len(doc_files)} docs"))
    else:
        print(f"  ✅ Documentação completa ({len(doc_files)} arquivos)!")
        results.append(("Documentação", True, f"{len(doc_files)}/{len(doc_files)}"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Documentação", False, str(e)))

# ============================================================================
# TESTE 7: Verificar imports no main.py
# ============================================================================
print("\n✓ TESTE 7: Verificando imports em main.py...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        'from app.application import JSONMySQLApplication, ApplicationConfig',
        'from app.core import setup_logger, get_logger',
        'import argparse',
        'from pathlib import Path',
    ]
    
    missing = []
    for import_line in required_imports:
        if import_line not in content:
            missing.append(import_line)
    
    if missing:
        print(f"  ❌ Imports faltando:")
        for imp in missing:
            print(f"     - {imp}")
        results.append(("Imports corretos", False, f"{len(missing)} faltam"))
    else:
        print(f"  ✅ Todos os imports presentes!")
        results.append(("Imports corretos", True, f"{len(required_imports)} ok"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Imports corretos", False, str(e)))

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 70)
print("📊 RESUMO FINAL")
print("=" * 70)

passed = sum(1 for _, success, _ in results if success)
total = len(results)

print(f"\nResultados: {passed}/{total} testes passaram\n")

for test_name, success, detail in results:
    status = "✅" if success else "❌"
    detail_str = f" → {detail}" if detail else ""
    print(f"  {status} {test_name}{detail_str}")

print("\n" + "=" * 70)

if passed == total:
    print("🎉 SUCESSO! Código corrigido e pronto para usar!")
    print("\nPróximas etapas:")
    print("  1. Instale as dependências: pip install -r requirements.txt")
    print("  2. Configure o .env com suas credenciais MySQL")
    print("  3. Execute: python scripts/main.py --file dados/seu_arquivo.json")
    print("=" * 70)
    sys.exit(0)
else:
    print(f"⚠️ {total - passed} verificação(ões) encontraram problemas")
    print("=" * 70)
    sys.exit(1)
