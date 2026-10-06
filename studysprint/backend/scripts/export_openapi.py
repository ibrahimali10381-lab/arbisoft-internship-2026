"""Write the OpenAPI spec to docs/openapi.json: `python scripts/export_openapi.py`."""

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.main import app  # noqa: E402

target = BACKEND.parent / "docs" / "openapi.json"
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(app.openapi(), indent=2) + "\n")
print(f"wrote {target}")
