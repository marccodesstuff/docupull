"""Benchmark runner: field-level accuracy/precision/recall and latency."""

from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

from core.pipeline import run
from core.schema.lab_report import LabReport

from benchmark.generate_synthetic import generate_dataset


def _truth_field(truth: dict[str, Any], name: str) -> Any:
    if name == "panel":
        return [a["analyte"] for a in truth.get("panel", [])]
    return truth.get(name)


def _pred_field(schema: dict[str, Any], name: str) -> Any:
    if name == "panel":
        return [a.get("analyte") for a in schema.get("panel", [])]
    return schema.get(name)


def evaluate(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    latencies: list[float] = []
    required = list(LabReport.model_fields.keys())
    per_field: dict[str, dict[str, int]] = {name: {"tp": 0, "fp": 0, "fn": 0} for name in required}

    for record in records:
        pdf = str(record["digital_pdf"])
        truth = record["truth"]
        start = time.perf_counter()
        result = run(pdf)
        latencies.append(time.perf_counter() - start)
        pred = result["schema"]

        row: dict[str, Any] = {"patient_id": record["patient_id"], "overall_status": result["overall_status"], "fields": {}}
        for name in required:
            t = _truth_field(truth, name)
            p = _pred_field(pred, name)
            match = t == p
            if name in ("patient_id", "report_date", "ordering_provider"):
                per_field[name]["tp"] += int(match)
                per_field[name]["fp"] += int(not match)
                per_field[name]["fn"] += int(not match)
            else:
                t_set = set(t) if isinstance(t, list) else set()
                p_set = set(p) if isinstance(p, list) else set()
                tp = len(t_set & p_set)
                fp = len(p_set - t_set)
                fn = len(t_set - p_set)
                per_field[name]["tp"] += tp
                per_field[name]["fp"] += fp
                per_field[name]["fn"] += fn
            row["fields"][name] = {"truth": t, "pred": p, "match": match}
        rows.append(row)

    summary_fields: dict[str, dict[str, float]] = {}
    for name, counts in per_field.items():
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        summary_fields[name] = {"precision": precision, "recall": recall, "f1": 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0}

    return {
        "n": len(records),
        "latency_p50": statistics.median(latencies) if latencies else 0.0,
        "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0,
        "fields": summary_fields,
        "rows": rows,
    }


def print_table(summary: dict[str, Any]) -> None:
    print(f"Processed {summary['n']} documents.")
    print(f"Latency p50: {summary['latency_p50']:.3f}s | p95: {summary['latency_p95']:.3f}s")
    print("| Field | Precision | Recall | F1 |")
    print("| --- | --- | --- | --- |")
    for name, values in summary["fields"].items():
        print(f"| {name} | {values['precision']:.2f} | {values['recall']:.2f} | {values['f1']:.2f} |")


def main() -> None:
    out_dir = os.environ.get("DOCUPULL_OUTPUT_DIR", "./tmp/outputs")
    dataset_path = Path(out_dir) / "dataset.json"
    if not dataset_path.exists():
        generate_dataset(output_dir=out_dir)
    records = json.loads(dataset_path.read_text())
    summary = evaluate(records)
    print_table(summary)


if __name__ == "__main__":
    main()
