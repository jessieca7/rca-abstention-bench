from pathlib import Path

import pytest

from rca_abstention_bench.schema import Question, load_questions

ROOT = Path(__file__).resolve().parents[1]


def test_seed_questions_load():
    questions = load_questions(ROOT / "data" / "questions.json")
    assert len(questions) >= 7
    assert {q.category.value for q in questions} >= {"answerable", "false_premise"}


def test_answerable_needs_root_cause():
    with pytest.raises(ValueError):
        Question(id="x", question="q", answerable=True, category="answerable")


def test_unanswerable_needs_reason():
    with pytest.raises(ValueError):
        Question(id="x", question="q", answerable=False, category="missing_evidence")


def test_category_must_match_answerable_flag():
    with pytest.raises(ValueError):
        Question(id="x", question="q", answerable=False, category="answerable",
                 unanswerable_reason="r")
