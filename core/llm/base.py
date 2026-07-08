from __future__ import annotations

from pydantic import BaseModel


class BaseLLMClient:
    def generate_structured(self, *, prompt: str, schema: type[BaseModel]) -> BaseModel:
        raise NotImplementedError
