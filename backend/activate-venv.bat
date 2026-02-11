@echo off
REM Script de ativação automática da venv para Windows
REM Executa: activate-venv.bat script.py [args...]

if "%1"=="" (
    echo.
    echo ========================================
    echo Uso: activate-venv.bat script.py [args]
    echo ========================================
    echo.
    echo Exemplos:
    echo   activate-venv.bat scripts/main.py --file dados/arquivo.json
    echo   activate-venv.bat PROVA_SIMPLES.py
    echo.
    exit /b 1
)

REM Ativa a venv
call .venv\Scripts\activate.bat

REM Executa o script com os argumentos
python %*

REM Desativa a venv ao sair
call .venv\Scripts\deactivate.bat
