import json
from types import SimpleNamespace

from rca_abstention_bench.config import Settings
from rca_abstention_bench.llm import LLMClient


class FakeOpenAI:
    """Mimics client.chat.completions.create() without any network call."""

    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages, temperature, **extra):
        self.last_extra = extra
        message = SimpleNamespace(content="fake reply")
        usage = SimpleNamespace(prompt_tokens=5, completion_tokens=2)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


def test_complete_returns_text_and_logs(tmp_path):
    log = tmp_path / "calls.jsonl"
    settings = Settings(base_url="x", model="fake-model", api_key="k", log_path=log)
    client = LLMClient(settings=settings, client=FakeOpenAI())

    reply = client.complete("hi", system="be brief", tag="t1")

    assert reply.text == "fake reply"
    assert reply.prompt_tokens == 5
    record = json.loads(log.read_text().splitlines()[0])
    assert record["tag"] == "t1"
    assert record["prompt"] == "hi"
    assert record["model"] == "fake-model"


def test_json_mode_sends_response_format(tmp_path):
    settings = Settings(base_url="x", model="m", api_key="k", log_path=tmp_path / "c.jsonl")
    fake = FakeOpenAI()
    LLMClient(settings=settings, client=fake).complete("hi", json_mode=True)
    assert fake.last_extra == {"response_format": {"type": "json_object"}}
