"""
Sistema de rastreamento de uploads JSON.

Evita reuploads de arquivos duplicados usando hash SHA256.
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import text, Column, String, DateTime, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def calculate_file_hash(file_path: Path) -> str:
    """
    Calcula o hash SHA256 de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        Hash SHA256 em hexadecimal
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class UploadTracker:
    """Gerencia rastreamento de uploads no banco de dados."""
    
    def __init__(self, engine):
        """
        Inicializa o rastreador.
        
        Args:
            engine: SQLAlchemy Engine
        """
        self.engine = engine
        self._ensure_tracking_table()
    
    def _ensure_tracking_table(self):
        """Cria a tabela de rastreamento se não existir."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS uploads_tracking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_hash VARCHAR(64) NOT NULL UNIQUE,
            table_name VARCHAR(255) NOT NULL,
            rows_inserted INT NOT NULL DEFAULT 0,
            file_size_bytes BIGINT NOT NULL,
            upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            execution_time_seconds FLOAT NOT NULL,
            status VARCHAR(50) NOT NULL,
            error_message TEXT,
            INDEX idx_file_hash (file_hash),
            INDEX idx_upload_date (upload_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text(create_table_sql))
                connection.commit()
        except Exception as e:
            print(f"⚠️ Aviso ao criar tabela de rastreamento: {e}")
    
    def file_already_uploaded(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Verifica se um arquivo já foi feito upload.
        
        Args:
            file_path: Caminho do arquivo
        
        Returns:
            Dicionário com informações do upload anterior, ou None
        """
        file_hash = calculate_file_hash(file_path)
        
        query = text("""
            SELECT id, file_name, table_name, rows_inserted, upload_date, status
            FROM uploads_tracking
            WHERE file_hash = :file_hash AND status = 'success'
            ORDER BY upload_date DESC
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, {"file_hash": file_hash}).fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'file_name': result[1],
                        'table_name': result[2],
                        'rows_inserted': result[3],
                        'upload_date': result[4],
                        'status': result[5],
                        'file_hash': file_hash
                    }
        except Exception as e:
            print(f"⚠️ Erro ao verificar arquivo: {e}")
        
        return None
    
    def register_upload(self, file_path: Path, table_name: str, rows_inserted: int, 
                       execution_time: float, status: str = 'success', 
                       error_message: Optional[str] = None) -> bool:
        """
        Registra um upload na tabela de rastreamento.
        
        Args:
            file_path: Caminho do arquivo
            table_name: Nome da tabela
            rows_inserted: Número de linhas inseridas
            execution_time: Tempo de execução em segundos
            status: Status do upload (success, error, partial)
            error_message: Mensagem de erro, se houver
        
        Returns:
            True se registrado com sucesso
        """
        file_hash = calculate_file_hash(file_path)
        file_size = file_path.stat().st_size
        
        insert_sql = text("""
            INSERT INTO uploads_tracking 
            (file_name, file_hash, table_name, rows_inserted, file_size_bytes, 
             execution_time_seconds, status, error_message, upload_date)
            VALUES 
            (:file_name, :file_hash, :table_name, :rows_inserted, :file_size, 
             :exec_time, :status, :error_msg, :upload_date)
        """)
        
        try:
            with self.engine.connect() as connection:
                connection.execute(insert_sql, {
                    'file_name': file_path.name,
                    'file_hash': file_hash,
                    'table_name': table_name,
                    'rows_inserted': rows_inserted,
                    'file_size': file_size,
                    'exec_time': execution_time,
                    'status': status,
                    'error_msg': error_message,
                    'upload_date': datetime.now()
                })
                connection.commit()
                return True
        except Exception as e:
            print(f"❌ Erro ao registrar upload: {e}")
            return False
    
    def get_upload_history(self, limit: int = 10) -> list:
        """
        Obtém histórico de uploads recentes.
        
        Args:
            limit: Número máximo de registros
        
        Returns:
            Lista de uploads
        """
        query = text("""
            SELECT file_name, table_name, rows_inserted, upload_date, status
            FROM uploads_tracking
            ORDER BY upload_date DESC
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as connection:
                results = connection.execute(query, {"limit": limit}).fetchall()
                return [
                    {
                        'file_name': r[0],
                        'table_name': r[1],
                        'rows_inserted': r[2],
                        'upload_date': r[3],
                        'status': r[4]
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"⚠️ Erro ao obter histórico: {e}")
            return []
