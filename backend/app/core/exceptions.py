"""
Exceções customizadas da aplicação.

Segue padrão de hierarquia bem definida para tratamento específico.
"""


class JSONMySQLException(Exception):
    """Exceção base de todas as exceções da aplicação."""
    pass


class ConfigurationError(JSONMySQLException):
    """Erro na configuração."""
    pass


class DatabaseError(JSONMySQLException):
    """Erro relacionado ao banco de dados."""
    pass


class ConnectionError(DatabaseError):
    """Erro na conexão com banco."""
    pass


class ValidationError(JSONMySQLException):
    """Erro na validação de dados."""
    pass


class SchemaError(JSONMySQLException):
    """Erro no schema da tabela."""
    pass


class LoaderError(JSONMySQLException):
    """Erro durante o carregamento de dados."""
    pass


class ParsingError(JSONMySQLException):
    """Erro ao fazer parsing de JSON."""
    pass


class NormalizationError(JSONMySQLException):
    """Erro na normalização de dados."""
    pass


class FileNotFoundError(JSONMySQLException):
    """Arquivo não encontrado."""
    pass


class InvalidFormatError(JSONMySQLException):
    """Formato de arquivo inválido."""
    pass
