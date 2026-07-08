from __future__ import annotations

from abc import ABC

from pydantic import BaseModel


class DocumentSchema(ABC, BaseModel):
    @classmethod
    def schema_required_fields(cls) -> list[str]:
        return [name for name, field in cls.model_fields.items() if field.is_required()]
