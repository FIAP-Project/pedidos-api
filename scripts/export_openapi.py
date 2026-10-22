"""Gera o openapi.yaml a partir da aplicação. Uso: python scripts/export_openapi.py"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.main import app  # noqa: E402

destino = Path(__file__).resolve().parent.parent / "openapi.yaml"
destino.write_text(yaml.safe_dump(app.openapi(), sort_keys=False, allow_unicode=True), encoding="utf-8")
print(f"OpenAPI gerado em {destino}")
