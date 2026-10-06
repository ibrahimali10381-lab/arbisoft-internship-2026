"""Write the demo lecture PDF to sample_data/: `python scripts/make_sample_pdf.py`."""

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.demo import SAMPLE_FILENAME, sample_pdf  # noqa: E402

target = BACKEND.parent / "sample_data" / SAMPLE_FILENAME
target.parent.mkdir(exist_ok=True)
target.write_bytes(sample_pdf())
print(f"wrote {target}")
