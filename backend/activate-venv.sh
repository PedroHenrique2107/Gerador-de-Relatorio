#!/bin/bash
# Script de ativação automática da venv para macOS/Linux
# Executa: ./activate-venv.sh script.py [args...]

if [ "$#" -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Uso: ./activate-venv.sh script.py [args]"
    echo "========================================"
    echo ""
    echo "Exemplos:"
    echo "  ./activate-venv.sh scripts/main.py --file dados/arquivo.json"
    echo "  ./activate-venv.sh PROVA_SIMPLES.py"
    echo ""
    exit 1
fi

# Ativa a venv
source .venv/bin/activate

# Executa o script com os argumentos
python "$@"

# Desativa a venv ao sair
deactivate
