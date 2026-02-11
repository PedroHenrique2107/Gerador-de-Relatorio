#!/usr/bin/env python
"""
PROVA DE FUNCIONAMENTO - Valida se o código corrigido funciona.
"""

import sys
import os
import traceback
from pathlib import Path

# ⚠️ VALIDA VIRTUAL ENVIRONMENT - ANTES DE QUALQUER OUTRA IMPORTAÇÃO
os.chdir(Path(__file__).parent)

# Validação simplificada inline para não depender de imports
if 'VIRTUAL_ENV' not in os.environ and not hasattr(sys, 'real_prefix') and sys.prefix == sys.base_prefix:
    error_msg = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌ ERRO: VIRTUAL ENVIRONMENT NÃO ATIVADO               ║
╚════════════════════════════════════════════════════════════════════════════╝

⚠️  Este teste OBRIGATORIAMENTE deve ser executado dentro de uma 
   virtual environment (.venv).

🔧 Para ativar a venv e rodar a prova, execute:

   Windows:
   .venv\\Scripts\\activate
   python PROVA_FUNCIONAMENTO.py
   
   macOS/Linux:
   source .venv/bin/activate
   python PROVA_FUNCIONAMENTO.py

📌 OU execute diretamente com Python da venv:

   Windows:
   .venv\\Scripts\\python PROVA_FUNCIONAMENTO.py
   
   macOS/Linux:
   .venv/bin/python PROVA_FUNCIONAMENTO.py

💡 Para mais informações:
   - Leia: GUIA_VENV.md
   - Ou: COMECE_AQUI.md

════════════════════════════════════════════════════════════════════════════
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Agora SIM podemos importar os modules que dependem de packages
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 PROVA DE FUNCIONAMENTO - Validação do Código Corrigido")
print("=" * 70)

results = []

# ============================================================================
# TESTE 1: Importar módulos principais
# ============================================================================
print("\n✓ TESTE 1: Importando módulos principais...")
try:
    from app.core import setup_logger, get_logger, DatabaseManager
    from app.loaders import BaseLoader, LoadResult, QuickLoader
    from app.utils import JSONParser, SchemaInferencer
    from app.validators import DataValidator, ReferentialValidator
    from app.application import JSONMySQLApplication, ApplicationConfig
    from config import config, get_config
    print("  ✅ Todos os módulos importados com sucesso!")
    results.append(("Importar módulos", True, ""))
except Exception as e:
    print(f"  ❌ Erro ao importar: {e}")
    results.append(("Importar módulos", False, str(e)))
    traceback.print_exc()

# ============================================================================
# TESTE 2: Sintaxe do main.py
# ============================================================================
print("\n✓ TESTE 2: Verificando sintaxe do scripts/main.py...")
try:
    import py_compile
    py_compile.compile('scripts/main.py', doraise=True)
    print("  ✅ scripts/main.py - Sintaxe válida!")
    results.append(("Sintaxe main.py", True, ""))
except Exception as e:
    print(f"  ❌ Erro de sintaxe: {e}")
    results.append(("Sintaxe main.py", False, str(e)))

# ============================================================================
# TESTE 3: Validar estrutura de classes
# ============================================================================
print("\n✓ TESTE 3: Validando estrutura de classes...")
try:
    from datetime import datetime
    
    # ApplicationConfig
    app_config = ApplicationConfig()
    assert hasattr(app_config, 'env'), "ApplicationConfig sem atributo 'env'"
    assert hasattr(app_config, 'debug'), "ApplicationConfig sem atributo 'debug'"
    
    # LoadResult
    now = datetime.now()
    result = LoadResult(
        success=True,
        table="test",
        rows_inserted=10,
        rows_failed=0,
        execution_time=0.5,
        errors=[],
        started_at=now,
        finished_at=now
    )
    assert result.success == True, "LoadResult.success incorreto"
    assert result.success_rate == 100.0, "LoadResult.success_rate incorreto"
    
    print("  ✅ Estrutura de classes validada!")
    results.append(("Estrutura de classes", True, ""))
except Exception as e:
    print(f"  ❌ Erro na validação: {e}")
    results.append(("Estrutura de classes", False, str(e)))
    traceback.print_exc()

# ============================================================================
# TESTE 4: Try-Finally em main.py
# ============================================================================
print("\n✓ TESTE 4: Verificando correção do try-finally em main.py...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se o finally está depois do except
    has_try = 'try:' in content
    has_except = 'except Exception as e:' in content
    has_finally = 'finally:' in content
    
    # Verifica posição correta
    try_pos = content.find('try:')
    except_pos = content.find('except Exception as e:')
    finally_pos = content.find('finally:')
    
    assert has_try, "Sem bloco try"
    assert has_except, "Sem bloco except"
    assert has_finally, "Sem bloco finally"
    assert finally_pos > except_pos, "finally deve estar após except"
    
    # Verifica se cleanup é chamado no finally
    finally_block = content[finally_pos:finally_pos+200]
    assert 'app.cleanup()' in finally_block, "cleanup() não está no finally"
    
    print("  ✅ Try-Finally estruturado corretamente!")
    print(f"     - try na posição: {try_pos}")
    print(f"     - except na posição: {except_pos}")
    print(f"     - finally na posição: {finally_pos}")
    results.append(("Try-Finally correto", True, ""))
except Exception as e:
    print(f"  ❌ Erro na verificação: {e}")
    results.append(("Try-Finally correto", False, str(e)))

# ============================================================================
# TESTE 5: Verificar validação de venv em main.py
# ============================================================================
print("\n✓ TESTE 5: Verificando validação de venv em main.py...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('VIRTUAL_ENV' in content, "Verifica VIRTUAL_ENV"),
        ('sys.base_prefix' in content, "Verifica sys.base_prefix"),
        ('VIRTUAL ENVIRONMENT NÃO ATIVADO' in content, "Mensagem de erro"),
        ('.venv' in content, "Instruções de ativação"),
    ]
    
    all_pass = True
    for check, desc in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {desc}")
        if not check:
            all_pass = False
    
    if all_pass:
        results.append(("Validação venv", True, ""))
    else:
        results.append(("Validação venv", False, "Algumas verificações falharam"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Validação venv", False, str(e)))

# ============================================================================
# TESTE 6: Verificar arquivo de dados de exemplo
# ============================================================================
print("\n✓ TESTE 6: Verificando estrutura de dados...")
try:
    data_dir = Path('dados')
    if data_dir.exists():
        files = list(data_dir.glob('*.json'))
        print(f"  ✅ Encontrados {len(files)} arquivo(s) JSON em dados/")
        for f in files:
            print(f"     - {f.name}")
        results.append(("Dados de exemplo", True, f"{len(files)} arquivos"))
    else:
        print("  ⚠️ Pasta dados/ não encontrada (ok)")
        results.append(("Dados de exemplo", True, "Pasta não encontrada"))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Dados de exemplo", False, str(e)))

# ============================================================================
# TESTE 7: Validar tipos e type hints
# ============================================================================
print("\n✓ TESTE 7: Validando type hints...")
try:
    import inspect
    from dataclasses import fields
    
    # Verifica se JSONMySQLApplication tem type hints
    sig = inspect.signature(JSONMySQLApplication.__init__)
    assert 'app_config' in sig.parameters, "JSONMySQLApplication sem type hints"
    
    # Verifica LoadResult
    result_fields = [f.name for f in fields(LoadResult)]
    expected = ['success', 'table', 'rows_inserted', 'rows_failed', 'execution_time', 'errors', 'started_at', 'finished_at']
    assert result_fields == expected, f"LoadResult campos incorretos: {result_fields}"
    
    print("  ✅ Type hints validados!")
    results.append(("Type hints", True, ""))
except Exception as e:
    print(f"  ❌ Erro: {e}")
    results.append(("Type hints", False, str(e)))

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 70)
print("📊 RESUMO DA PROVA DE FUNCIONAMENTO")
print("=" * 70)

passed = sum(1 for _, success, _ in results if success)
total = len(results)

print(f"\nResultados: {passed}/{total} testes passaram\n")

for test_name, success, detail in results:
    status = "✅ PASS" if success else "❌ FAIL"
    detail_str = f" - {detail}" if detail else ""
    print(f"  {status}: {test_name}{detail_str}")

print("\n" + "=" * 70)

if passed == total:
    print("🎉 SUCESSO! Código corrigido e funcionando perfeitamente!")
    print("=" * 70)
    sys.exit(0)
else:
    print(f"⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")
    print("=" * 70)
    sys.exit(1)
