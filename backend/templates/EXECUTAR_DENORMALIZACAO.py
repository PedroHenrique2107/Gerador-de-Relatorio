#!/usr/bin/env python3
"""
Script para executar denormalização quando MySQL estiver disponível.
Valida conexão e executa scripts/denormalize_inplace.py
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
    print("\nAbra um terminal e execute:")
    print("  Windows:  .venv\\Scripts\\activate")
    print("  Linux:    source .venv/bin/activate")
    print("="*70 + "\n")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import DatabaseManager, get_logger

logger = get_logger(__name__)

print("\n" + "="*80)
print("VERIFICAÇÃO PRE-EXECUÇÃO")
print("="*80)

# Tenta conectar ao MySQL
print("\n[1/3] Testando conexão MySQL...")
try:
    from config.settings import AppConfig
    config = AppConfig(env="development")
    DatabaseManager.initialize(config)
    engine = DatabaseManager.get_engine()
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("      [OK] MySQL conectado!")
except Exception as e:
    print(f"      [ERRO] {str(e)[:60]}")
    print("\nMySQL nao esta acessivel!")
    print("Verifique:")
    print("  • Servidor MySQL esta rodando?")
    print("  • Credenciais em .env estao corretas?")
    print("  • Firewall nao esta bloqueando porta 3306?")
    sys.exit(1)

# Valida arquivos de entrada
print("\n[2/3] Validando arquivos JSON...")
json_file = Path('data/ExtratoClienteHistorico.json')
if not json_file.exists():
    print(f"      [ERRO] {json_file} nao encontrado")
    sys.exit(1)
print(f"      [OK] {json_file}")

# Importa script
print("\n[3/3] Importando script denormalizacao...")
try:
    from scripts.denormalize_inplace import denormalize_extrato_inplace
    print("      [OK] Script importado")
except Exception as e:
    print(f"      [ERRO] {e}")
    sys.exit(1)

print("\n" + "="*80)
print("INICIANDO DENORMALIZACAO IN-PLACE")
print("="*80)

try:
    denormalize_extrato_inplace(json_file)
    print("\n[SUCESSO] Denormalizacao concluida!")
    print("\nProximos passos:")
    print("  1. Abra DBForge")
    print("  2. Conecte em dev_pricing database")
    print("  3. Abra tabela ExtratoClienteHistorico")
    print("  4. Deve ter 18.885 linhas (era 7.039)")
    print("  5. Cada parcela agora eh uma linha separada")
except Exception as e:
    print(f"\n[ERRO] {str(e)}")
    logger.exception("Erro na denormalizacao")
    sys.exit(1)

print("\n" + "="*80)
