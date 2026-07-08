from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyteResult(BaseModel):
    analyte: str = Field(..., description="Analyte name")
    value: float | str = Field(..., description="Measured value")
    unit: str | None = Field(default=None, description="Unit")
    reference_range: str | None = Field(default=None, description="Reference range")
    flag: str | None = Field(default=None, description="Value flag: normal / H / L")


class LabReport(BaseModel):
    patient_id: str = Field(..., description="Synthetic patient identifier")
    report_date: str = Field(..., description="Report date")
    ordering_provider: str | None = Field(default=None, description="Ordering provider")
    panel: list[AnalyteResult] = Field(default_factory=list, description="Analyte results")
