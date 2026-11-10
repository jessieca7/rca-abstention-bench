"""Run the whole pilot with your local model and save results to results/pilot/.

    uv run python scripts/run_pilot.py
"""

import argparse
import sys
from pathlib import Path

from rca_abstention_bench.llm import LLMClient
from rca_abstention_bench.pilot import run_all, save_results
from rca_abstention_bench.pilot_data import PROJECT_ROOT

parser = argparse.ArgumentParser()
parser.add_argument("--runs", type=int, default=3, help="repeats per question")
parser.add_argument("--temperature", type=float, default=0.5)
parser.add_argument("--out", default=str(PROJECT_ROOT / "results" / "pilot"))
args = parser.parse_args()

client = LLMClient()
try:  # fail fast with a clear message if the model server is not running
    client.complete("Reply with the single word OK.", tag="preflight")
except Exception as error:
    sys.exit(f"Could not reach the model at {client.settings.base_url}: {error}\n"
             "Is Ollama running? Try: ollama serve")

trials = run_all(client, args.runs, args.temperature)
meta = {"model": client.settings.model, "runs": args.runs, "temperature": args.temperature}
summary = save_results(trials, Path(args.out), meta)
print(f"\nSaved results to {args.out}")
print((Path(args.out) / "summary.md").read_text())
