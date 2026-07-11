"""Structured extraction: build a schema-aware prompt and call the LLM."""

from __future__ import annotations

from pydantic import BaseModel

from core.llm.factory import build_client
from core.schema.lab_report import LabReport


def _schema_summary(schema: type[BaseModel]) -> str:
    fields = []
    for name, info in schema.model_fields.items():
        fields.append(f"- {name}: {info.annotation}")
    return "\n".join(fields)


def build_prompt(*, text: str, schema: type[BaseModel]) -> str:
    return (
        "Extract data from the following document text into JSON matching the schema.\n"
        f"Schema fields:\n{_schema_summary(schema)}\n\n"
        f"Document text:\n{text}\n"
    )


def extract_structured(*, text: str, schema: type[BaseModel] = LabReport) -> BaseModel:
    client = build_client()
    prompt = build_prompt(text=text, schema=schema)
    return client.generate_structured(prompt=prompt, schema=schema)
