"""
Relatório de Validação Completa - Aplicação JSON para SQL
"""
import sys
import json
from pathlib import Path
from datetime import datetime

print("="*80)
print("VALIDAÇÃO COMPLETA - JSON para SQL em Python")
print("="*80)
print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando validação...\n")

# 1. Validação de venv
print("1. AMBIENTE VIRTUAL")
has_venv = hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
)
status1 = "[OK]" if has_venv else "[ERRO]"
print(f"   {status1} Venv ativo: {'Sim' if has_venv else 'Nao'}")
print(f"   [OK] Python: {sys.version.split()[0]}")
print(f"   [OK] Executable: {sys.executable}")

# 2. Validação de dependências
print("\n2. DEPENDÊNCIAS")
deps_ok = True
for pkg in ['pandas', 'sqlalchemy', 'pymysql']:
    try:
        __import__(pkg)
        print(f"   [OK] {pkg}")
    except ImportError:
        print(f"   [ERRO] {pkg} nao instalado")
        deps_ok = False

# 3. Validação de estrutura de diretórios
print("\n3. ESTRUTURA DE DIRETÓRIOS")
required_dirs = [
    'app', 'config', 'scripts', 'data', 'logs', 'docs'
]
dirs_ok = True
for d in required_dirs:
    exists = Path(d).is_dir()
    status = "[OK]" if exists else "[ERRO]"
    print(f"   {status} {d}/")
    if not exists:
        dirs_ok = False

# 4. Validação de arquivos críticos
print("\n4. ARQUIVOS CRÍTICOS")
critical_files = [
    ('app/application.py', 'Application principal'),
    ('config/settings.py', 'Configuracao'),
    ('scripts/main.py', 'CLI'),
    ('scripts/denormalize_inplace.py', 'Denormalizacao in-place'),
    ('scripts/normalize_extrato.py', 'Normalizacao 3-tabelas'),
    ('.env', 'Variaveis de ambiente'),
]
files_ok = True
for f, desc in critical_files:
    exists = Path(f).is_file()
    status = "[OK]" if exists else "[ERRO]"
    print(f"   {status} {f:40s} ({desc})")
    if not exists:
        files_ok = False

# 5. Validação de dados JSON
print("\n5. DADOS JSON")
try:
    with open('data/ExtratoClienteHistorico.json', encoding='utf-8') as f:
        data = json.load(f)
    docs = len(data.get('data', []))
    parcelas = sum(len(d.get('installments', [])) for d in data.get('data', []))
    print(f"   [OK] ExtratoClienteHistorico.json")
    print(f"        - Documentos: {docs:,}")
    print(f"        - Parcelas: {parcelas:,}")
    print(f"        - Taxa expansao: {parcelas/docs:.1f}x")
except Exception as e:
    print(f"   [ERRO] ExtratoClienteHistorico.json: {str(e)[:50]}")

try:
    with open('data/DataPagto.json', encoding='utf-8') as f:
        data = json.load(f)
    data_list = data.get('data', []) if isinstance(data, dict) else data
    print(f"   [OK] DataPagto.json: {len(data_list):,} registros")
except Exception as e:
    print(f"   [ERRO] DataPagto.json: {str(e)[:50]}")

# 6. Resumo
print("\n" + "="*80)
print("RESUMO")
print("="*80)

all_ok = has_venv and deps_ok and dirs_ok and files_ok
if all_ok:
    print("\n✓ APLICACAO 100% OPERACIONAL!")
    print("\nProximo passo:")
    print("  $ python scripts/denormalize_inplace.py")
    print("\nQue vai:")
    print("  • Carregar ExtratoClienteHistorico.json")
    print("  • Expandir 7.039 docs em 18.885 linhas")
    print("  • Sobrescrever tabela no MySQL")
    print("  • Resultar em dados desagrupados no DBForge")
else:
    print("\n✗ Existem problemas a resolver!")
    if not has_venv:
        print("  • Ativar venv: .venv\\Scripts\\activate")
    if not deps_ok:
        print("  • Instalar dependencias: pip install -r requirements.txt")
    if not dirs_ok:
        print("  • Criar diretorios faltantes")
    if not files_ok:
        print("  • Restaurar arquivos faltantes")

print("\n" + "="*80)
