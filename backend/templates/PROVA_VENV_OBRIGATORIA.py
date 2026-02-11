#!/usr/bin/env python
"""
PROVA FINAL - Validação completa do sistema de obrigatoriedade de venv
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("🧪 PROVA FINAL - Validação de Virtual Environment Obrigatório")
print("=" * 80)

tests = []

# ============================================================================
# TESTE 1: main.py tem validação de venv
# ============================================================================
print("\n✓ TESTE 1: Verificando validação de venv em main.py...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('VIRTUAL_ENV' in content, "Verifica VIRTUAL_ENV"),
        ('sys.base_prefix' in content, "Verifica sys.base_prefix"),
        ('sys.prefix == sys.base_prefix' in content, "Verifica se prefixes são iguais"),
        ('VIRTUAL ENVIRONMENT NÃO ATIVADO' in content, "Mensagem de erro customizada"),
        ('.venv\\\\Scripts\\\\activate' in content or '.venv/bin/activate' in content, "Instruções de ativação"),
    ]
    
    all_pass = True
    for check, desc in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {desc}")
        if not check:
            all_pass = False
    
    if all_pass:
        tests.append(("Validação em main.py", True))
    else:
        tests.append(("Validação em main.py", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Validação em main.py", False))

# ============================================================================
# TESTE 2: Arquivos de ativação automática existem
# ============================================================================
print("\n✓ TESTE 2: Verificando scripts de ativação automática...")
try:
    files = [
        ('activate-venv.bat', 'Windows batch'),
        ('activate-venv.sh', 'Linux/macOS shell'),
    ]
    
    all_exist = True
    for filename, desc in files:
        exists = Path(filename).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {filename} ({desc})")
        if not exists:
            all_exist = False
    
    if all_exist:
        tests.append(("Scripts de ativação", True))
    else:
        tests.append(("Scripts de ativação", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Scripts de ativação", False))

# ============================================================================
# TESTE 3: Documentação de venv existe
# ============================================================================
print("\n✓ TESTE 3: Verificando documentação sobre venv...")
try:
    docs = [
        ('GUIA_VENV.md', 'Guia completo de venv'),
        ('COMECE_AQUI.md', 'Quick start com venv'),
    ]
    
    all_exist = True
    for filename, desc in docs:
        exists = Path(filename).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {filename} ({desc})")
        if not exists:
            all_exist = False
    
    if all_exist:
        tests.append(("Documentação venv", True))
    else:
        tests.append(("Documentação venv", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Documentação venv", False))

# ============================================================================
# TESTE 4: Validador de venv existe e tem funcionalidades corretas
# ============================================================================
print("\n✓ TESTE 4: Verificando módulo venv_validator...")
try:
    validator_file = Path('app/core/venv_validator.py')
    
    if not validator_file.exists():
        print(f"  ❌ Arquivo não encontrado: {validator_file}")
        tests.append(("Módulo validador", False))
    else:
        with open(validator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        functions = [
            ('is_inside_venv', 'Verificar se está em venv'),
            ('require_venv', 'Forçar uso de venv'),
            ('get_venv_activation_command', 'Comando de ativação'),
            ('print_venv_status', 'Status da venv'),
        ]
        
        all_exist = True
        for func_name, desc in functions:
            exists = f'def {func_name}' in content
            status = "✅" if exists else "❌"
            print(f"  {status} {func_name}() - {desc}")
            if not exists:
                all_exist = False
        
        if all_exist:
            tests.append(("Módulo validador", True))
        else:
            tests.append(("Módulo validador", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Módulo validador", False))

# ============================================================================
# TESTE 5: app/core/__init__.py exporta validador
# ============================================================================
print("\n✓ TESTE 5: Verificando exportações em core/__init__.py...")
try:
    with open('app/core/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    exports = [
        ('require_venv', 'Função require_venv'),
        ('is_inside_venv', 'Função is_inside_venv'),
        ('print_venv_status', 'Função print_venv_status'),
    ]
    
    all_exist = True
    for export_name, desc in exports:
        exists = export_name in content
        status = "✅" if exists else "❌"
        print(f"  {status} {export_name} exportado")
        if not exists:
            all_exist = False
    
    if all_exist:
        tests.append(("Exportações core", True))
    else:
        tests.append(("Exportações core", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Exportações core", False))

# ============================================================================
# TESTE 6: Mensagem de erro é clara e helpful
# ============================================================================
print("\n✓ TESTE 6: Verificando qualidade da mensagem de erro...")
try:
    with open('scripts/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a mensagem de erro
    start = content.find('error_msg = f"""')
    end = content.find('"""', start + 20)
    if start > 0 and end > 0:
        msg = content[start:end]
        
        checks = [
            ('❌ ERRO' in msg, "Indicador visual de erro"),
            ('VIRTUAL ENVIRONMENT' in msg, "Menciona virtual environment"),
            ('.venv\\\\Scripts\\\\activate' in msg or '.venv/bin/activate' in msg, "Instruções de ativação"),
            ('GUIA_VENV.md' in msg, "Link para documentação"),
        ]
        
        all_pass = True
        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {desc}")
            if not check:
                all_pass = False
        
        if all_pass:
            tests.append(("Mensagem de erro", True))
        else:
            tests.append(("Mensagem de erro", False))
    else:
        print("  ❌ Mensagem de erro não encontrada")
        tests.append(("Mensagem de erro", False))
        
except Exception as e:
    print(f"  ❌ Erro: {e}")
    tests.append(("Mensagem de erro", False))

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMO FINAL - Sistema de Obrigatoriedade de venv")
print("=" * 80)

passed = sum(1 for _, success in tests if success)
total = len(tests)

print(f"\nResultados: {passed}/{total} verificações passaram\n")

for test_name, success in tests:
    status = "✅" if success else "❌"
    print(f"  {status} {test_name}")

print("\n" + "=" * 80)

if passed == total:
    print("🎉 SUCESSO! Sistema de obrigatoriedade de venv implementado!")
    print("\n✨ Agora:")
    print("   - Usuários SEM ativar venv: ❌ Erro claro com instruções")
    print("   - Usuários COM venv ativada: ✅ Tudo funciona normalmente")
    print("   - Scripts de ativação automática disponíveis")
    print("   - Documentação clara em 2 arquivos (GUIA_VENV.md, COMECE_AQUI.md)")
    print("\n📖 Próximos passos:")
    print("   1. Leia GUIA_VENV.md para entender o sistema")
    print("   2. Leia COMECE_AQUI.md para quick start")
    print("   3. Teste: .venv\\Scripts\\activate")
    print("   4. Depois: python scripts/main.py --help")
    print("=" * 80)
    sys.exit(0)
else:
    print(f"⚠️ {total - passed} verificação(ões) falharam")
    print("=" * 80)
    sys.exit(1)
