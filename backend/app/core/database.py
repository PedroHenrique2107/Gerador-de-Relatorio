"""
Camada de banco de dados com Pool e engine SQLAlchemy.

Implementa padrão Singleton para gerenciamento de conexões.
"""

from typing import Optional, Generator
from sqlalchemy import create_engine, text, inspect, Engine
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from app.core.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Gerenciador de conexões com banco de dados."""
    
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[Engine] = None
    
    def __new__(cls):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, database_url: str, **kwargs) -> None:
        """
        Inicializa engine.
        
        Args:
            database_url: URL SQLAlchemy do banco
            **kwargs: Argumentos adicionais para create_engine
        """
        instance = cls()
        
        if instance._engine is not None:
            logger.warning("Engine já inicializado. Ignorando inicialização dupla.")
            return
        
        try:
            instance._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=kwargs.get('pool_size', 10),
                max_overflow=kwargs.get('max_overflow', 20),
                pool_timeout=kwargs.get('pool_timeout', 30),
                pool_recycle=kwargs.get('pool_recycle', 3600),
                echo=kwargs.get('echo', False),
                future=True,
            )
            logger.info("Engine SQLAlchemy inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar engine: {e}")
            raise
    
    @classmethod
    def get_engine(cls) -> Engine:
        """
        Retorna engine SQLAlchemy.
        
        Returns:
            Engine: Engine configurado
        
        Raises:
            RuntimeError: Se engine não foi inicializado
        """
        instance = cls()
        if instance._engine is None:
            raise RuntimeError(
                "Engine não inicializado. Chame DatabaseManager.initialize() primeiro."
            )
        return instance._engine
    
    @classmethod
    @contextmanager
    def connection(cls):
        """
        Context manager para gerenciar conexão.
        
        Exemplo:
            >>> with DatabaseManager.connection() as conn:
            ...     result = conn.execute(text("SELECT 1"))
        """
        engine = cls.get_engine()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    @classmethod
    @contextmanager
    def session(cls):
        """
        Context manager para gerenciar transação.
        
        Exemplo:
            >>> with DatabaseManager.session() as session:
            ...     # commit automático ao sair do bloco
            ...     pass
        """
        from sqlalchemy.orm import Session
        
        engine = cls.get_engine()
        session = Session(engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erro na transação: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def execute(cls, query: str) -> list:
        """
        Executa query SQL.
        
        Args:
            query: SQL query como string
        
        Returns:
            list: Resultados da query
        """
        with cls.connection() as conn:
            result = conn.execute(text(query))
            return result.fetchall()
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Testa conexão com banco.
        
        Returns:
            bool: True se conexão OK
        """
        try:
            with cls.connection() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexão com banco testada com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False
    
    @classmethod
    def get_inspector(cls) -> inspect.Inspector:
        """
        Retorna inspector para inspecionar estrutura do banco.
        
        Returns:
            Inspector: Inspector do SQLAlchemy
        """
        return inspect(cls.get_engine())
    
    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        """
        Verifica se tabela existe.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            bool: True se existe
        """
        inspector = cls.get_inspector()
        return table_name in inspector.get_table_names()
    
    @classmethod
    def get_table_columns(cls, table_name: str) -> list:
        """
        Retorna colunas de uma tabela.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            list: Lista de nomes de colunas
        """
        inspector = cls.get_inspector()
        return [col['name'] for col in inspector.get_columns(table_name)]
    
    @classmethod
    def dispose(cls) -> None:
        """Fecha todas as conexões."""
        instance = cls()
        if instance._engine:
            instance._engine.dispose()
            instance._engine = None
            logger.info("Engine disposed")


# Atalho para evitar verbosidade
def get_engine() -> Engine:
    """Retorna engine de forma mais simples."""
    return DatabaseManager.get_engine()
