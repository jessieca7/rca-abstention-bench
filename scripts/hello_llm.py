"""Smoke test: send one prompt to the configured model and print the reply."""

from rca_abstention_bench.llm import LLMClient

client = LLMClient()
reply = client.complete(
    "In one sentence: what is a root cause analysis in site reliability engineering?",
    tag="hello",
)
print(f"model:   {reply.model}")
print(f"latency: {reply.latency_s}s")
print(f"tokens:  {reply.prompt_tokens} in / {reply.completion_tokens} out")
print(f"reply:   {reply.text}")
