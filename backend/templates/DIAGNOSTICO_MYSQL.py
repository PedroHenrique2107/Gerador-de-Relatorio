#!/usr/bin/env python3
"""
Diagnóstico de conexão com MySQL
"""

import sys
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("\n" + "="*80)
print("DIAGNÓSTICO DE CONEXÃO MySQL")
print("="*80)

# 1. Lê credenciais
print("\n[1/4] Lendo .env...")
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("MYSQL_HOST")
port = int(os.getenv("MYSQL_PORT", 3306))
user = os.getenv("MYSQL_USER")
db = os.getenv("MYSQL_DATABASE")

print(f"      Host: {host}")
print(f"      Port: {port}")
print(f"      User: {user}")
print(f"      DB:   {db}")

# 2. Testa DNS
print("\n[2/4] Testando DNS...")
try:
    ip = socket.gethostbyname(host)
    print(f"      [OK] {host} resolvido para {ip}")
except socket.gaierror as e:
    print(f"      [ERRO] DNS falhou: {e}")
    print("\n      Possíveis causas:")
    print("      • Servidor offline")
    print("      • Problema de DNS/rede")
    print("      • Firewall bloqueando")
    sys.exit(1)

# 3. Testa conexão de rede
print("\n[3/4] Testando conexão na porta...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"      [OK] Porta {port} está aberta")
    else:
        print(f"      [ERRO] Não conseguiu conectar na porta {port}")
        print("      Verifique firewall/network rules")
        sys.exit(1)
except Exception as e:
    print(f"      [ERRO] {e}")
    sys.exit(1)
finally:
    sock.close()

# 4. Testa MySQL
print("\n[4/4] Testando conexão MySQL...")
try:
    import pymysql
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=os.getenv("MYSQL_PASSWORD"),
        database=db,
        connect_timeout=10
    )
    print(f"      [OK] Conectado com sucesso!")
    
    # Testa query simples
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"      MySQL version: {version[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"      [ERRO] {e}")
    print("\n      Possíveis causas:")
    print("      • Credenciais incorretas")
    print("      • Usuário sem acesso")
    print("      • Database não existe")
    sys.exit(1)

print("\n" + "="*80)
print("✓ TUDO OK - Pronto para upload!")
print("="*80 + "\n")
