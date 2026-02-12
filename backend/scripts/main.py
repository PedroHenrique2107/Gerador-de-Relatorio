#!/usr/bin/env python
"""
Script principal - CLI para carregar JSON em MySQL.

Uso:
    python scripts/main.py --file data/arquivo.json --table minha_tabela
    python scripts/main.py --dir data/ --pattern "*.json"
"""

import sys
import os
from pathlib import Path

# âš ï¸ VALIDA VIRTUAL ENVIRONMENT - ANTES DE QUALQUER OUTRA IMPORTAÃ‡ÃƒO
# Isso deve ser feito ANTES de importar modules que dependem de packages
os.chdir(Path(__file__).parent.parent)

# ValidaÃ§Ã£o simplificada inline para nÃ£o depender de imports
if 'VIRTUAL_ENV' not in os.environ and not hasattr(sys, 'real_prefix') and sys.prefix == sys.base_prefix:
    error_msg = f"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                    âŒ ERRO: VIRTUAL ENVIRONMENT NÃƒO ATIVADO               â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

âš ï¸  Este projeto OBRIGATORIAMENTE deve ser executado dentro de uma 
   virtual environment (.venv).

ðŸ”§ Para ativar a venv e usar a aplicaÃ§Ã£o, execute:

   Windows:
   .venv\\Scripts\\activate
   
   macOS/Linux:
   source .venv/bin/activate

ðŸ“Œ OU execute diretamente com Python da venv:

   Windows:
   .venv\\Scripts\\python {' '.join(sys.argv[1:])}
   
   macOS/Linux:
   .venv/bin/python {' '.join(sys.argv[1:])}

ðŸ’¡ Para mais informaÃ§Ãµes:
   - Leia: GUIA_VENV.md
   - Ou: COMECE_AQUI.md

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Agora SIM podemos importar os modules que dependem de packages
import argparse

# Adiciona root ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application import JSONMySQLApplication, ApplicationConfig
from app.core import setup_logger, get_logger

logger = setup_logger('main')


def main():
    """FunÃ§Ã£o principal."""
    parser = argparse.ArgumentParser(
        description='Carrega arquivos JSON em MySQL'
    )
    
    # Modo: arquivo Ãºnico ou diretÃ³rio
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file',
        type=Path,
        help='Arquivo JSON para carregar'
    )
    input_group.add_argument(
        '--dir',
        type=Path,
        help='DiretÃ³rio com arquivos JSON'
    )
    
    # OpÃ§Ãµes
    parser.add_argument(
        '--table',
        type=str,
        help='Nome da tabela (auto se nÃ£o especificado)'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.json',
        help='PadrÃ£o de arquivo (default: *.json)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='quick',
        choices=['quick', 'load', 'upsert'],
        help='Modo de carregamento'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=5000,
        help='Tamanho do chunk'
    )
    parser.add_argument(
        '--if-exists',
        type=str,
        default='append',
        choices=['fail', 'replace', 'append'],
        help='AÃ§Ã£o se tabela existe'
    )
    parser.add_argument(
        '--env',
        type=str,
        default='development',
        choices=['development', 'testing', 'production'],
        help='Ambiente'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Ativa modo debug'
    )
    parser.add_argument(
        '--lines',
        action='store_true',
        help='Trata como NDJSON (newline-delimited)'
    )
    
    args = parser.parse_args()
    
    app = None
    try:
        # Inicializa aplicaÃ§Ã£o
        app_config = ApplicationConfig(
            env=args.env,
            debug=args.debug,
            loader_mode=args.mode,
            chunk_size=args.chunk_size,
        )
        
        app = JSONMySQLApplication(app_config)
        
        # Carrega arquivo(s)
        if args.file:
            logger.info(f"Carregando arquivo: {args.file}")
            # Define o nome da tabela:
            # - Se o usuÃ¡rio informou --table, usa esse nome
            # - SenÃ£o, usa o nome do arquivo sem extensÃ£o
            table_name = args.table or args.file.stem
            
            result = app.load_json(
                args.file,
                table_name,
                lines=args.lines,
                if_exists=args.if_exists,
            )
            
            print(f"\n{'='*60}")
            print(f"Resultado: {result}")
            print(f"{'='*60}\n")
            
            return 0 if result.success else 1
        
        elif args.dir:
            logger.info(f"Carregando diretÃ³rio: {args.dir}")
            
            files = sorted(Path(args.dir).glob(args.pattern))
            if not files:
                logger.error(f"Nenhum arquivo encontrado: {args.dir}/{args.pattern}")
                return 1
            
            results = app.load_multiple(
                files,
                lines=args.lines,
                if_exists=args.if_exists,
            )
            
            print(f"\n{'='*60}")
            print(f"Resumo: {len(results)} arquivos carregados")
            for result in results:
                print(f"  {'OK' if result.success else 'ERRO'} {result}")
            print(f"{'='*60}\n")
            
            return 0 if all(r.success for r in results) else 1
    
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return 1
    
    finally:
        if app:
            app.cleanup()


if __name__ == '__main__':
    sys.exit(main())
