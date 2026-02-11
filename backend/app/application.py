"""
Aplicação principal - Orquestra todos os componentes.

Este é o ponto de entrada para operações de carregamento.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.core import get_logger, DatabaseManager
from app.loaders import QuickLoader, LoadResult
from app.utils import JSONParser, SchemaInferencer
from config import config, get_config

logger = get_logger(__name__)


@dataclass
class ApplicationConfig:
    """Configuração da aplicação."""
    env: str = "development"
    debug: bool = False
    loader_mode: str = "quick"  # quick, load, upsert
    chunk_size: int = 5000
    validate_before_insert: bool = True
    normalize_nested: bool = False
    
    def __post_init__(self):
        """Carrega configuração do arquivo."""
        cfg = get_config(self.env)
        self.debug = cfg.debug or self.debug


class JSONMySQLApplication:
    """Aplicação principal para carregar JSON em MySQL."""
    
    def __init__(self, app_config: Optional[ApplicationConfig] = None):
        """
        Inicializa aplicação.
        
        Args:
            app_config: Configuração da aplicação
        """
        self.app_config = app_config or ApplicationConfig()
        self.cfg = get_config(self.app_config.env)
        
        # Inicializa banco
        DatabaseManager.initialize(
            self.cfg.database.url,
            pool_size=self.cfg.database.pool_size,
            max_overflow=self.cfg.database.max_overflow,
            echo=self.cfg.debug,
        )
        
        # Testa conexão
        if not DatabaseManager.test_connection():
            raise RuntimeError("Falha ao conectar no banco de dados")
        
        logger.info("✓ Aplicação inicializada com sucesso")
    
    def load_json(
        self,
        file_path: Path,
        table_name: str,
        **kwargs,
    ) -> LoadResult:
        """
        Carrega arquivo JSON em tabela MySQL.
        
        Args:
            file_path: Caminho do arquivo JSON
            table_name: Nome da tabela
            **kwargs: Argumentos adicionais (lines, if_exists, etc)
        
        Returns:
            LoadResult: Resultado do carregamento
        
        Exemplo:
            >>> app = JSONMySQLApplication()
            >>> result = app.load_json(
            ...     Path("dados/my_file.json"),
            ...     "my_table",
            ...     lines=False,
            ...     if_exists="replace"
            ... )
            >>> print(result)
        """
        file_path = Path(file_path)
        
        logger.info(f"Iniciando carregamento: {file_path} → {table_name}")
        
        # Usa QuickLoader (implementar outros depois)
        loader = QuickLoader(self.app_config.__dict__)
        
        try:
            result = loader.load(
                file_path,
                table_name,
                chunk_size=self.app_config.chunk_size,
                **kwargs,
            )
            
            if result.success:
                logger.info(f"✓ {result}")
            else:
                logger.error(f"✗ {result}")
            
            return result
        
        except Exception as e:
            logger.error(f"Erro ao carregar: {e}")
            raise
    
    def load_multiple(
        self,
        files: List[Path],
        table_names: Optional[List[str]] = None,
        **kwargs,
    ) -> List[LoadResult]:
        """
        Carrega múltiplos arquivos JSON.
        
        Args:
            files: Lista de caminhos
            table_names: Lista de nomes de tabela (opcional)
            **kwargs: Argumentos adicionais
        
        Returns:
            List[LoadResult]: Resultados de cada carregamento
        """
        if table_names is None:
            table_names = [f.stem for f in files]
        
        results = []
        for file_path, table_name in zip(files, table_names):
            result = self.load_json(file_path, table_name, **kwargs)
            results.append(result)
        
        return results
    
    def infer_schema(self, file_path: Path, sample_size: int = 100) -> str:
        """
        Infere schema SQL a partir de arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo
            sample_size: Número de registros para amostrar
        
        Returns:
            str: Comando CREATE TABLE
        """
        file_path = Path(file_path)
        
        logger.info(f"Inferindo schema: {file_path}")
        
        # Parse JSON (amostra)
        data = JSONParser.parse_file(file_path, sample_size=sample_size)
        
        # Converter para DataFrame
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Gerar DDL
        table_name = file_path.stem
        ddl = SchemaInferencer.generate_create_table(
            table_name,
            df,
            indexes=['created_at', 'updated_at'],
        )
        
        logger.info(f"✓ Schema inferido para {table_name}")
        return ddl
    
    def create_table(self, table_name: str, ddl: str) -> bool:
        """
        Cria tabela no banco.
        
        Args:
            table_name: Nome da tabela
            ddl: Comando CREATE TABLE
        
        Returns:
            bool: Sucesso
        """
        try:
            logger.info(f"Criando tabela: {table_name}")
            DatabaseManager.execute(ddl)
            logger.info(f"✓ Tabela criada: {table_name}")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao criar tabela: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Retorna informações sobre uma tabela.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            Dict com informações
        """
        inspector = DatabaseManager.get_inspector()
        
        return {
            'name': table_name,
            'exists': DatabaseManager.table_exists(table_name),
            'columns': DatabaseManager.get_table_columns(table_name),
            'row_count': self._get_row_count(table_name),
        }
    
    @staticmethod
    def _get_row_count(table_name: str) -> int:
        """Retorna número de registros."""
        try:
            result = DatabaseManager.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            return result[0][0] if result else 0
        except:
            return 0
    
    def cleanup(self) -> None:
        """Limpa recursos."""
        DatabaseManager.dispose()
        logger.info("Aplicação finalizada")
