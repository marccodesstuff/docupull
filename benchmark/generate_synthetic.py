"""Synthetic lab-report dataset generator."""

from __future__ import annotations

import json
import os
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from docupull.core.schema.lab_report import AnalyteResult, LabReport


ANALYTES = [
    {"analyte": "Glucose", "value": 95.0, "unit": "mg/dL", "reference_range": "70-99", "flag": "normal"},
    {"analyte": "Cholesterol", "value": 180.0, "unit": "mg/dL", "reference_range": "<200", "flag": "normal"},
    {"analyte": "HDL", "value": 55.0, "unit": "mg/dL", "reference_range": ">40", "flag": "normal"},
    {"analyte": "LDL", "value": 110.0, "unit": "mg/dL", "reference_range": "<130", "flag": "normal"},
]


def build_lab_report(patient_id: str, report_date: str, ordering_provider: str) -> LabReport:
    return LabReport(
        patient_id=patient_id,
        report_date=report_date,
        ordering_provider=ordering_provider,
        panel=[AnalyteResult.model_validate(a) for a in ANALYTES],
    )


def render_pdf(path: Path, report: LabReport) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Lab Report", styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(f"Patient: {report.patient_id}", styles["Normal"]))
    story.append(Paragraph(f"Date: {report.report_date}", styles["Normal"]))
    story.append(Paragraph(f"Provider: {report.ordering_provider or ''}", styles["Normal"]))
    story.append(Spacer(1, 12))
    data = [["Analyte", "Value", "Unit", "Reference", "Flag"]]
    for a in report.panel:
        data.append([a.analyte, str(a.value), a.unit or "", a.reference_range or "", a.flag or ""])
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#c0c0c0"),
        ("GRID", (0, 0), (-1, -1), 1, "#000"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    doc.build(story)


def generate_dataset(*, output_dir: str | None = None, count: int = 5) -> list[dict[str, object]]:
    base = Path(output_dir or os.environ.get("DOCUPULL_OUTPUT_DIR", "./tmp/outputs"))
    base.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for i in range(count):
        pid = f"SYN-{i + 1:03d}"
        report_date = f"2026-07-{i + 1:02d}"
        report = build_lab_report(patient_id=pid, report_date=report_date, ordering_provider="Dr. Bot")
        digital_path = base / f"digital_{pid}.pdf"
        render_pdf(digital_path, report)
        records.append({
            "patient_id": pid,
            "report_date": report_date,
            "ordering_provider": "Dr. Bot",
            "digital_pdf": str(digital_path),
            "truth": report.model_dump(),
        })
    out_json = base / "dataset.json"
    out_json.write_text(json.dumps(records, indent=2))
    return records


def main() -> None:
    records = generate_dataset()
    print(f"Generated {len(records)} synthetic lab reports.")


if __name__ == "__main__":
    main()
