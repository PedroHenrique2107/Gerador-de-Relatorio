"""
Configuração centralizada da aplicação.

Esta é a única fonte de verdade para todas as configurações.
Segue o padrão 12-factor app (https://12factor.net/)
"""

import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from dotenv import load_dotenv
from urllib.parse import quote

# Carrega .env no início
load_dotenv()


class Environment(str, Enum):
    """Ambientes de execução."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LoaderMode(str, Enum):
    """Modos de carregamento disponíveis."""
    QUICK = "quick"          # Insert simples, 940 linhas/seg
    LOAD = "load"            # LOAD DATA, 3.900 linhas/seg
    UPSERT = "upsert"        # UPSERT inteligente


class ChunkSize(int, Enum):
    """Tamanhos padrão de chunk por modo."""
    QUICK = 5000
    LOAD = 10000
    UPSERT = 1000


@dataclass
class DatabaseConfig:
    """Configuração de banco de dados."""
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @property
    def url(self) -> str:
        """Retorna URL SQLAlchemy com encoding de caracteres especiais."""
        password_encoded = quote(self.password, safe='')
        return (
            f"mysql+pymysql://{self.user}:{password_encoded}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )


@dataclass
class LoggerConfig:
    """Configuração de logging."""
    level: str = "INFO"
    format: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_dir: Path = Path("logs")
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5


@dataclass
class ProcessingConfig:
    """Configuração de processamento."""
    default_chunk_size: int = 5000
    max_memory_mb: int = 512
    max_file_size_mb: int = 2048
    validate_before_insert: bool = True
    normalize_nested: bool = True
    use_local_infile: bool = False


@dataclass
class AppConfig:
    """Configuração completa da aplicação."""
    
    # Ambiente
    env: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Banco de dados
    database: DatabaseConfig = None
    
    # Logging
    logger: LoggerConfig = None
    
    # Processamento
    processing: ProcessingConfig = None
    
    # Caminhos
    root_dir: Path = Path(__file__).parent.parent
    data_dir: Path = Path("data")
    output_dir: Path = Path("output")
    
    def __post_init__(self):
        """Inicializa valores padrão."""
        if self.database is None:
            self.database = DatabaseConfig(
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", 3306)),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                database=os.getenv("MYSQL_DATABASE", ""),
                echo=self.debug,
            )
        
        if self.logger is None:
            self.logger = LoggerConfig(
                level="DEBUG" if self.debug else "INFO",
                log_dir=self.root_dir / "logs",
            )
        
        if self.processing is None:
            self.processing = ProcessingConfig(
                use_local_infile=os.getenv("MYSQL_LOCAL_INFILE", "0") == "1",
                validate_before_insert=not self.debug,
            )
    
    def validate(self) -> None:
        """Valida configuração."""
        if not self.database.user:
            raise ValueError("MYSQL_USER não configurado")
        if not self.database.database:
            raise ValueError("MYSQL_DATABASE não configurado")
        
        # Cria diretórios se não existirem
        self.logger.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


def get_config(env: Optional[str] = None) -> AppConfig:
    """
    Retorna configuração com base no ambiente.
    
    Args:
        env: Nome do ambiente (development, testing, production)
             Se None, usa variável ENV ou padrão
    
    Returns:
        AppConfig: Configuração da aplicação
    """
    from dotenv import load_dotenv
    
    # Carrega .env
    load_dotenv()
    
    # Determina ambiente
    env = env or os.getenv("ENV", "development")
    environment = Environment(env.lower())
    
    # Cria configuração
    config = AppConfig(
        env=environment,
        debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
    )
    
    # Valida
    config.validate()
    
    return config


# Singleton da configuração
_config: Optional[AppConfig] = None


def config() -> AppConfig:
    """Retorna instância única de configuração."""
    global _config
    if _config is None:
        _config = get_config()
    return _config
