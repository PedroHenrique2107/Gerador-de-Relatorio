"""
Gerador XLS - Usando openpyxl em modo write-only para performance
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from pathlib import Path

class XLSGenerator:
    """Gera arquivo Excel (.xlsx) otimizado"""
    
    def generate(self, rows, filepath):
        """
        Gera arquivo Excel
        
        Args:
            rows: Lista de dicionários com dados
            filepath: Caminho do arquivo de saída
        """
        
        if not rows:
            raise ValueError("Nenhum dado para exportar")
        
        # Criar workbook
        wb = Workbook(write_only=True)
        ws = wb.create_sheet('Relatório')
        
        # Cabeçalhos
        headers = list(rows[0].keys())
        ws.append(headers)
        
        # Dados
        for row in rows:
            ws.append(list(row.values()))
        
        # Salvar
        wb.save(filepath)
