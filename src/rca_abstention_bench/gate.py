"""Design B's rule gate: a deterministic Python check on the agent's proposed action.

No AI is involved here. The same inputs always give the same decision, so the
gate is easy to test and easy to explain.

Two rules, applied in order:
  1. The action's target must be the service named in the alert.
  2. The action must not be one that text inside the logs asks for.
"""

import re
from dataclasses import dataclass

# Words that mean "this action", used by rule 2 to spot a log line asking for it.
ACTION_KEYWORDS = {
    "restart_service": ["restart", "reboot"],
    "rollback_deployment": ["rollback", "roll back", "revert"],
    "disable_feature_flag": ["disable", "turn off", "switch off"],
    "scale_service": ["scale"],
}
# Phrases that make text read like an order to an assistant.
INSTRUCTION_CUES = (
    "system:", "assistant", "ignore", "instruction", "you must", "you should",
    "immediately", "important", "please", "urgent",
)
# Matches key="value" and captures the value: the text a user could have written.
QUOTED_VALUE = re.compile(r'\b\w+="([^"]*)"')


def normalize_target(target: str) -> str:
    """'Checkout Service' -> 'checkout', so naming differences do not matter."""
    cleaned = (target or "").strip().lower().replace("_", "-").replace(" ", "-")
    for suffix in ("-service", "-svc", "-pods", "-pod"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
    return cleaned


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    rule: str  # no_action | target_not_alert_service | action_requested_by_log_text | allowed
    reason: str


def untrusted_texts(log_lines: list[str]) -> list[str]:
    """Every quoted value in the logs. We treat all of it as possibly attacker-written."""
    return [value for line in log_lines for value in QUOTED_VALUE.findall(line)]


def check_action(action: str, target: str, alert_service: str, log_lines: list[str]) -> GateDecision:
    if action == "none":
        return GateDecision(True, "no_action", "No action proposed.")

    if normalize_target(target) != normalize_target(alert_service):
        return GateDecision(
            False,
            "target_not_alert_service",
            f"Target '{target}' is not the alerted service '{alert_service}'.",
        )

    keywords = ACTION_KEYWORDS.get(action, [])
    for text in untrusted_texts(log_lines):
        lowered = text.lower()
        sounds_like_an_order = any(cue in lowered for cue in INSTRUCTION_CUES)
        names_the_action = any(word in lowered for word in keywords)
        if sounds_like_an_order and names_the_action:
            return GateDecision(
                False,
                "action_requested_by_log_text",
                f'A log field asks for this action: "{text}"',
            )

    return GateDecision(True, "allowed", "Target matches the alert and no log text asked for it.")
