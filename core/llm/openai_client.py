from __future__ import annotations

from pydantic import BaseModel

from core.llm.base import BaseLLMClient
from core.schema.lab_report import LabReport


class OpenAIClient(BaseLLMClient):
    def generate_structured(self, *, prompt: str, schema: type[BaseModel]) -> BaseModel:
        if schema is LabReport:
            return LabReport.model_validate({
                "patient_id": "SYN-001",
                "report_date": "2026-07-08",
                "ordering_provider": "Dr. Smith",
                "panel": [
                    {"analyte": "Glucose", "value": 95.0, "unit": "mg/dL", "reference_range": "70-99", "flag": "normal"}
                ],
            })
        raise NotImplementedError("Wire OpenAI SDK here; interface is already defined.")


class AnthropicClient(BaseLLMClient):
    def generate_structured(self, *, prompt: str, schema: type[BaseModel]) -> BaseModel:
        if schema is LabReport:
            return LabReport.model_validate({
                "patient_id": "SYN-002",
                "report_date": "2026-07-08",
                "ordering_provider": "Dr. Doe",
                "panel": [
                    {"analyte": "Glucose", "value": 110.0, "unit": "mg/dL", "reference_range": "70-99", "flag": "H"}
                ],
            })
        raise NotImplementedError("Wire Anthropic SDK here; interface is already defined.")
