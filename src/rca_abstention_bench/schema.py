"""The shape of one benchmark question, plus loading and validation.

Every question is labeled answerable or not. Unanswerable ones also carry the
reason category, so we can report abstention recall per type (Chart 2).
"""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, model_validator


class Category(str, Enum):
    ANSWERABLE = "answerable"
    MISSING_EVIDENCE = "missing_evidence"
    FALSE_PREMISE = "false_premise"
    OUT_OF_SCOPE = "out_of_scope"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    STALE_DATA = "stale_data"
    UNDERSPECIFIED = "underspecified"


class Split(str, Enum):
    DEV = "dev"    # ~20 questions, only for tuning the design-3 threshold
    TEST = "test"  # everything we report results on


class Question(BaseModel):
    id: str
    question: str
    answerable: bool
    category: Category
    root_cause: str | None = None            # required if answerable
    unanswerable_reason: str | None = None   # required if not answerable
    evidence_ids: list[str] = []             # kb file ids that support the label
    split: Split = Split.TEST
    verified: bool = False                   # True once a human has checked the label

    @model_validator(mode="after")
    def check_label_consistency(self):
        if self.answerable and self.category != Category.ANSWERABLE:
            raise ValueError(f"{self.id}: answerable=true needs category 'answerable'")
        if not self.answerable and self.category == Category.ANSWERABLE:
            raise ValueError(f"{self.id}: answerable=false needs an unanswerable category")
        if self.answerable and not self.root_cause:
            raise ValueError(f"{self.id}: answerable question needs root_cause")
        if not self.answerable and not self.unanswerable_reason:
            raise ValueError(f"{self.id}: unanswerable question needs unanswerable_reason")
        return self


def load_questions(path: str | Path) -> list[Question]:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    questions = [Question(**item) for item in items]
    ids = [q.id for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate question ids")
    return questions


def missing_evidence_files(questions: list[Question], kb_dir: str | Path) -> list[str]:
    """Return evidence ids that point to files not present under kb_dir."""
    kb_files = {p.stem for p in Path(kb_dir).rglob("*") if p.is_file()}
    return sorted({e for q in questions for e in q.evidence_ids if e not in kb_files})
