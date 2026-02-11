"""
Validador de Virtual Environment.

Verifica se o código está rodando dentro de uma venv e força sua ativação.
"""

import sys
import os
from pathlib import Path


def is_inside_venv() -> bool:
    """
    Verifica se o Python atual está rodando dentro de uma virtual environment.
    
    Returns:
        True se está dentro de venv, False caso contrário
    """
    # Método 1: Verificar VIRTUAL_ENV
    if 'VIRTUAL_ENV' in os.environ:
        return True
    
    # Método 2: Verificar sys.prefix
    if hasattr(sys, 'real_prefix'):
        return True
    
    # Método 3: Verificar se sys.base_prefix != sys.prefix
    if sys.prefix != sys.base_prefix:
        return True
    
    return False


def get_venv_activation_command() -> str:
    """
    Retorna o comando para ativar a venv dependendo do OS.
    
    Returns:
        Comando de ativação apropriado
    """
    if sys.platform == 'win32':
        return '.venv\\Scripts\\activate'
    else:
        return 'source .venv/bin/activate'


def get_venv_python_command() -> str:
    """
    Retorna o comando para rodar Python dentro da venv.
    
    Returns:
        Comando apropriado para o OS
    """
    if sys.platform == 'win32':
        return '.venv\\Scripts\\python'
    else:
        return '.venv/bin/python'


def require_venv() -> None:
    """
    Força o uso de virtual environment.
    
    Raises:
        RuntimeError: Se não estiver dentro de uma venv
    """
    if is_inside_venv():
        return  # Tudo ok, está na venv
    
    # Não está na venv, mostrar erro e sair
    error_message = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌ ERRO: VIRTUAL ENVIRONMENT NÃO ATIVADO               ║
╚════════════════════════════════════════════════════════════════════════════╝

⚠️  Este projeto OBRIGATORIAMENTE deve ser executado dentro de uma 
   virtual environment (.venv).

🔧 Para ativar a venv e usar a aplicação, execute:

   {get_venv_activation_command()}

📌 OU execute diretamente com Python da venv:

   {get_venv_python_command()} {' '.join(sys.argv)}

💡 Instruções completas:

   1. ATIVAR VENV (Windows):
      .venv\\Scripts\\activate
      
   2. ATIVAR VENV (macOS/Linux):
      source .venv/bin/activate
      
   3. VERIFICAR SE ATIVOU:
      pip list  (deve mostrar packages instalados)
      
   4. USAR A APLICAÇÃO:
      python scripts/main.py --file dados/arquivo.json --table tabela

⚙️  Dependências no projeto:
   - pandas>=2.0.0
   - SQLAlchemy>=2.0.0
   - PyMySQL>=1.1.0
   - python-dotenv>=1.0.0
   - E outras em requirements.txt

📖 Documentação: Veja MAPA_NAVEGACAO.md para mais detalhes

════════════════════════════════════════════════════════════════════════════
"""
    
    print(error_message, file=sys.stderr)
    sys.exit(1)


def print_venv_status() -> None:
    """Imprime status atual do virtual environment."""
    status = "✅ ATIVADO" if is_inside_venv() else "❌ NÃO ATIVADO"
    venv_path = os.environ.get('VIRTUAL_ENV', 'Não encontrado')
    python_exe = sys.executable
    
    print(f"""
📦 Status do Virtual Environment:
   Status: {status}
   Python: {python_exe}
   VIRTUAL_ENV: {venv_path}
   sys.prefix: {sys.prefix}
""")
