FROM python:3.11-slim

# Metadados
LABEL maintainer="Pedro Mendes"
LABEL description="JSON to MySQL Bulk Loader - Sistema profissional de carga em massa"

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (para MySQL client se necessário)
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY tests/ ./tests/
COPY .env.example .env.example
COPY README.md .
COPY QUICKSTART.md .

# Criar volumes para dados
VOLUME ["/data", "/logs"]

# Definir variáveis de ambiente default
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Comando padrão: mostrar help
ENTRYPOINT ["python", "-m", "src.json_to_mysql_quick"]
CMD ["--help"]

# Exemplo de uso:
# docker build -t json-mysql-bulk:latest .
# 
# Para carregar dados:
# docker run --env-file .env \
#   -v $(pwd)/dados:/data \
#   json-mysql-bulk \
#   --json-path /data/arquivo.ndjson \
#   --table minha_tabela \
#   --lines
