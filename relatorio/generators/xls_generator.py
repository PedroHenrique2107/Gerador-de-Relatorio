"""
Gerador XLS - Usando openpyxl em modo write-only para performance
"""

import re
from openpyxl import Workbook


def _format_numero_documento(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if re.fullmatch(r"\d+(\.0+)?", s):
        s = str(int(float(s)))
    if s.isdigit():
        return s.zfill(4)
    return s


class XLSGenerator:
    """Gera arquivo Excel (.xlsx) otimizado."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        wb = Workbook(write_only=True)
        ws = wb.create_sheet("Relatorio")

        headers = list(rows[0].keys())
        ws.append(headers)
        doc_idx = headers.index("NumeroDoDocumento") if "NumeroDoDocumento" in headers else -1

        for row in rows:
            values = list(row.values())
            if doc_idx >= 0:
                values[doc_idx] = _format_numero_documento(values[doc_idx])
            ws.append(values)

        wb.save(filepath)
