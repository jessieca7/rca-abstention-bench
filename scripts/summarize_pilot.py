"""Recompute the summary after you fill in the human_rc_correct column of review.csv.

    uv run python scripts/summarize_pilot.py
"""

import json
from pathlib import Path

from rca_abstention_bench.pilot import save_results
from rca_abstention_bench.pilot_data import PROJECT_ROOT
from rca_abstention_bench.scoring import read_human_verdicts

out = PROJECT_ROOT / "results" / "pilot"
trials = [json.loads(line) for line in (out / "trials.jsonl").read_text().splitlines() if line.strip()]
meta = json.loads((out / "meta.json").read_text())
human = read_human_verdicts(out / "review.csv")
save_results(trials, out, meta, human=human, write_review=False)
print(f"Used {len(human)} human verdicts out of {len(trials)} trials.\n")
print((out / "summary.md").read_text())
