#!/usr/bin/env python3
"""Debug da URL de conexão"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import AppConfig

config = AppConfig(env="development")
print(f"\nURL Montada:\n{config.database.url}\n")
