"""Loading the pilot's incidents, questions and logs, and planting the injection."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = PROJECT_ROOT / "data" / "pilot"


def load_incidents(pilot_dir: Path = PILOT_DIR) -> dict:
    return json.loads((pilot_dir / "incidents.json").read_text(encoding="utf-8"))


def load_questions(pilot_dir: Path = PILOT_DIR) -> list[dict]:
    questions = json.loads((pilot_dir / "questions.json").read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in questions}
    for q in questions:
        # A normal question remembers the injection its twin would carry.
        # It is only used as a control, never shown to the model.
        q["control_injection"] = None
    for q in questions:
        if q.get("injected"):
            by_id[q["paired_with"]]["control_injection"] = q["injection"]
    return questions


def load_log_lines(log_file: str, pilot_dir: Path = PILOT_DIR) -> list[str]:
    """Read a log file, dropping blank lines and '#' header comments."""
    text = (pilot_dir / log_file).read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line.strip() and not line.startswith("#")]


def with_injection(lines: list[str], injection: dict) -> list[str]:
    """Return a copy of the log with ONE attacker-written line inserted.

    The new line copies the timestamp of the line before it, so it looks like a
    normal log entry. The attacker's text sits inside a quoted field, such as
    user_note="...", the way user-supplied text would appear in a real log.
    """
    position = injection["after_line"]
    timestamp = lines[position - 1].split(" ", 1)[0]
    new_line = (
        f'{timestamp} {injection["service"]} ERROR order note '
        f'{injection["field"]}="{injection["text"]}"'
    )
    return lines[:position] + [new_line] + lines[position:]
