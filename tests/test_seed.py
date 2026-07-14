"""Smoke test for the synthetic seed generator.

Runs the generator with small sizes and asserts every gold table is produced with rows.
This is what CI exercises today; real per-layer tests land with each layer.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GOLD_TABLES = [
    "dim_consultant", "dim_client", "dim_job",
    "fact_pipeline", "fact_placements", "fact_bench", "fact_timesheets",
]


def test_seed_generates_all_gold_tables():
    result = subprocess.run(
        [sys.executable, "data/seed/generate_seed.py",
         "--consultants", "50", "--clients", "5", "--jobs", "20"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    out_dir = ROOT / "data" / "seed" / "out"
    for table in GOLD_TABLES:
        csv_path = out_dir / f"{table}.csv"
        assert csv_path.exists(), f"expected {csv_path} to be generated"
        # header line + at least one data row
        assert csv_path.read_text().count("\n") > 1, f"{table}.csv has no rows"
