#!/usr/bin/env python
"""
Runner: roda os testes e executa o script de upload para o banco.

Uso:
  python run_tests_and_upload.py --script normalize
  python run_tests_and_upload.py --script denormalize
  python run_tests_and_upload.py --no-tests --script normalize

Observações:
- A configuração do banco vem de variáveis de ambiente ou de um arquivo .env
  (o projeto já usa python-dotenv via `config.get_config`).
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_pytest():
    print("→ Executando testes com pytest...")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"]) 
    return r.returncode


def run_script(script_name: str) -> int:
    scripts = {
        'normalize': Path('scripts/normalize_extrato.py'),
        'denormalize': Path('scripts/denormalize_inplace.py'),
    }

    path = scripts.get(script_name)
    if path is None:
        print(f"Script desconhecido: {script_name}")
        return 2

    if not path.exists():
        print(f"Arquivo não encontrado: {path}")
        return 3

    print(f"→ Executando script: {path} (pode pedir venv ativado)")
    return subprocess.run([sys.executable, str(path)]).returncode


def main():
    p = argparse.ArgumentParser(description="Roda testes e faz upload para o banco")
    p.add_argument('--no-tests', action='store_true', help='Pular execução de testes')
    p.add_argument('--script', choices=['normalize', 'denormalize'], default='normalize')
    args = p.parse_args()

    # 1) Executa testes
    if not args.no_tests:
        rc = run_pytest()
        if rc != 0:
            print("✗ Alguns testes falharam. Abortando upload.")
            sys.exit(rc)
        print("✓ Testes passaram.")
    else:
        print("⚠ Pulando testes por opção (--no-tests).")

    # 2) Executa script de upload escolhido
    rc = run_script(args.script)
    if rc != 0:
        print(f"✗ Erro executando script ({args.script}), código: {rc}")
        sys.exit(rc)

    print("✓ Upload concluído com sucesso.")


if __name__ == '__main__':
    main()
