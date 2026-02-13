"""
Gerador CSV - Streaming para volumes grandes
"""

import csv


class CSVGenerator:
    """Gera arquivo CSV usando streaming."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        headers = list(rows[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
