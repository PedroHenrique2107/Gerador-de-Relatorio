"""
Gerador CSV - Streaming para volumes grandes
"""

import csv
from pathlib import Path

class CSVGenerator:
    """Gera arquivo CSV usando streaming"""
    
    def generate(self, rows, filepath):
        """
        Gera arquivo CSV
        
        Args:
            rows: Lista de dicionários com dados
            filepath: Caminho do arquivo de saída
        """
        
        if not rows:
            raise ValueError("Nenhum dado para exportar")
        
        # Cabeçalhos (pega chaves do primeiro registro)
        headers = list(rows[0].keys())
        
        # Escrever CSV em streaming
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=';')
            
            # Escrever cabeçalho
            writer.writeheader()
            
            # Escrever registros
            for row in rows:
                writer.writerow(row)
