from __future__ import annotations

import os

from core.llm.anthropic_client import AnthropicClient
from core.llm.base import BaseLLMClient
from core.llm.openai_client import OpenAIClient


def build_client(*, provider: str | None = None) -> BaseLLMClient:
    cfg = provider or os.environ.get("LLM_PROVIDER", "openai").lower()
    if cfg == "openai":
        return OpenAIClient()
    if cfg == "anthropic":
        return AnthropicClient()
    raise ValueError(f"Unsupported LLM provider: {cfg}")
