"""
Gerador CSV - Streaming para volumes grandes
"""

import csv
import re


def _format_numero_documento(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if re.fullmatch(r"\d+(\.0+)?", s):
        s = str(int(float(s)))
    if s.isdigit():
        s = s.zfill(4)
        # Mantem 0 a esquerda ao abrir CSV no Excel.
        return f'="{s}"'
    return s


class CSVGenerator:
    """Gera arquivo CSV usando streaming."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        headers = list(rows[0].keys())
        has_doc = "NumeroDoDocumento" in headers

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()

            for row in rows:
                row_out = dict(row)
                if has_doc:
                    row_out["NumeroDoDocumento"] = _format_numero_documento(
                        row_out.get("NumeroDoDocumento")
                    )
                writer.writerow(row_out)
