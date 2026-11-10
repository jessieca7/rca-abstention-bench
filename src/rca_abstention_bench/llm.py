"""One small wrapper around the chat API that every agent design will share.

Why a wrapper: all five designs must use the same model and settings, and every
call must be logged (question, raw output, latency, tokens) for the evaluation.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from rca_abstention_bench.config import Settings, load_settings


class LLMResponse(BaseModel):
    text: str
    model: str
    latency_s: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMClient:
    def __init__(self, settings: Settings | None = None, client: OpenAI | None = None):
        self.settings = settings or load_settings()
        # `client` can be injected in tests so no real model is needed.
        self._client = client or OpenAI(
            base_url=self.settings.base_url, api_key=self.settings.api_key
        )

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
        tag: str = "",
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send one prompt, return the reply, and append a record to the log.

        temperature=0 gives (mostly) repeatable answers; self-consistency
        will pass a higher value on purpose.
        `tag` is a free label (e.g. "design2:q017") to find the call in the log.
        json_mode=True asks the server to return valid JSON only.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        extra = {"response_format": {"type": "json_object"}} if json_mode else {}
        start = time.perf_counter()
        raw = self._client.chat.completions.create(
            model=self.settings.model,
            messages=messages,
            temperature=temperature,
            **extra,
        )
        latency = time.perf_counter() - start

        usage = getattr(raw, "usage", None)
        response = LLMResponse(
            text=raw.choices[0].message.content or "",
            model=self.settings.model,
            latency_s=round(latency, 3),
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )
        self._log(tag, system, prompt, temperature, response)
        return response

    def _log(self, tag, system, prompt, temperature, response: LLMResponse) -> None:
        path: Path = self.settings.log_path
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "tag": tag,
            "temperature": temperature,
            "system": system,
            "prompt": prompt,
            **response.model_dump(),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
