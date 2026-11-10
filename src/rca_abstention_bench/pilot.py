"""Run every pilot question several times and save the scored results."""

import csv
import json
import shutil
from pathlib import Path

from rca_abstention_bench.agent import run_trial
from rca_abstention_bench.pilot_data import load_incidents, load_log_lines, load_questions, with_injection
from rca_abstention_bench.retrieval import RunbookIndex
from rca_abstention_bench.scoring import render_markdown, summarize, write_review_csv


def run_all(client, runs: int, temperature: float, progress=print) -> list[dict]:
    incidents = load_incidents()
    questions = load_questions()
    index = RunbookIndex()
    trials = []
    for question in questions:
        incident = incidents[question["incident"]]
        logs = load_log_lines(incident["log_file"])
        if question["injected"]:
            logs = with_injection(logs, question["injection"])
        runbook_lines = index.search(incident["alert"] + " " + question["question"], k=4)
        for run in range(1, runs + 1):
            trial = run_trial(client, question, incident, logs, runbook_lines, run, temperature)
            trials.append(trial)
            progress(f'{question["id"]} run {run}: proposed {trial["proposed_action"]} '
                     f'({trial["proposed_target"]}), gate: {trial["gate_rule"]}')
    return trials


def save_results(trials: list[dict], out_dir: Path, meta: dict, human: dict | None = None,
                 write_review: bool = True) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "trials.jsonl").write_text("\n".join(json.dumps(t) for t in trials) + "\n", encoding="utf-8")
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    if write_review:
        review = out_dir / "review.csv"
        if review.exists():  # never overwrite a file a person may have filled in
            shutil.copy(review, out_dir / "review.previous.csv")
        write_review_csv(trials, review)

    summary = summarize(trials, human)
    (out_dir / "summary.md").write_text(
        render_markdown(summary, meta["model"], meta["runs"], meta["temperature"]), encoding="utf-8")
    with open(out_dir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["design", "injected_follow", "twin_control", "rc_normal", "rc_injected", "false_blocks"])
        for name, r in summary["designs"].items():
            writer.writerow([name, r["injected_follow"], r["twin_control"], r["rc_normal"],
                             r["rc_injected"], r["false_blocks"]])
    return summary
