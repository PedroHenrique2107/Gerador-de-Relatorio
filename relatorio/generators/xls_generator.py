"""
Gerador XLS - Usando openpyxl em modo write-only para performance
"""

from openpyxl import Workbook


class XLSGenerator:
    """Gera arquivo Excel (.xlsx) otimizado."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        wb = Workbook(write_only=True)
        ws = wb.create_sheet("Relatorio")

        headers = list(rows[0].keys())
        ws.append(headers)

        for row in rows:
            ws.append(list(row.values()))

        wb.save(filepath)
