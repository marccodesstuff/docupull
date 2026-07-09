# DocuPull

PDF → validated structured JSON with OCR fallback and per-field confidence scoring.

DocuPull ingests PDF documents and returns structured, schema-validated JSON. It automatically routes each page through the best available path: text-layer extraction when present, or OCR when the page is scanned/image-only. Every extracted field is confidence-scored, and documents with low-confidence required fields are flagged `needs_review` for human triage.

Target use case: medical lab reports (synthetic data only in this repo). The schema-driven design lets you add new document types without rewriting the pipeline.

## Why this exists

Most document-automation tooling either:
- assumes clean text-layer PDFs, or
- blindly OCRs everything.

DocuPull makes that choice per-page, based on real PDF internals, and it exposes confidence so downstream systems can route uncertain outputs to humans instead of silently wrong answers.

## What it does

- Detects digital vs scanned pages via text-density classification
- Extracts digital pages with PyMuPDF + pdfplumber tables
- OCRs scanned pages with OpenCV preprocessing + Tesseract, capturing per-word confidence
- Extracts structured data through a provider-agnostic LLM interface (OpenAI / Anthropic)
- Validates output against Pydantic schemas
- Scores per-field confidence from OCR confidence × deterministic cross-checks × validation
- Routes documents to `ok` or `needs_review` based on a configurable threshold

## Architecture

```
PDF ─▶ Ingest ─▶ Page Classifier ──digital──▶ PyMuPDF/pdfplumber text+tables ─┐
                      │                                                       ├─▶ LLM structured extract ─▶ Pydantic validate ─▶ Confidence score ─▶ ok / needs_review ─▶ JSON + report
                      └──scanned──▶ render 300dpi ▶ OpenCV preprocess ▶ Tesseract (+conf) ─┘
```

## Fallback decision tree

1. Measure text density per page with PyMuPDF.
2. If density ≥ `TEXT_DENSITY_THRESHOLD`, treat as digital.
3. Otherwise render to 300 DPI, preprocess with OpenCV, run Tesseract, and record mean word confidence.
4. If Tesseract mean confidence < `OCR_CONFIDENCE_THRESHOLD`, the page is low-quality and the final document can still be flagged `needs_review` by confidence scoring.
5. Merge per-page text, run structured extraction, validate, score confidence, apply `needs_review` rule.

All thresholds live in config with sensible defaults.

## Tech stack

- API: FastAPI + Uvicorn
- PDF: PyMuPDF + pdfplumber
- OCR: Tesseract via pytesseract, OpenCV preprocessing
- LLM: provider-agnostic interface; OpenAI + Anthropic implemented
- Validation: Pydantic v2
- Testing: pytest (+ pytest-mock)
- Lint/type/format: ruff, black, mypy
- Packaging/run: uv + Docker + docker-compose
- CI: GitHub Actions

## Quick start

```bash
cp .env.example .env
uv sync
PYTHONPATH=. uv run pytest -q
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Then visit:
- `GET /health`
- `POST /extract` with a PDF upload

## Configuration

Copy `.env.example` to `.env` and fill as needed:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-haiku-latest
TESSERACT_CMD=
TEXT_DENSITY_THRESHOLD=200
OCR_CONFIDENCE_THRESHOLD=60
FIELD_CONFIDENCE_THRESHOLD=0.75
DEBUG=false
LOG_LEVEL=INFO
UPLOAD_DIR=./tmp/uploads
OUTPUT_DIR=./tmp/outputs
```

Notes:
- `LLM_PROVIDER` must be `openai` or `anthropic`.
- `TESSERACT_CMD` is optional; if unset, pytesseract uses `/usr/bin/tesseract` or PATH lookup.
- `.env` is ignored by git.

## Docker

```bash
docker compose up --build
```

Image uses `python:3.11-slim` and installs system OCR dependencies. The API listens on `localhost:8000`.

## Running tests

```bash
PYTHONPATH=. uv run pytest -q
```

## Benchmark

```bash
PYTHONPATH=. uv run python benchmark/run_benchmark.py
```

This generates synthetic lab-report PDFs, runs the pipeline, and prints a field-level precision/recall/F1 table plus latency.

## Confidence scoring

`field_confidence = source_conf × cross_check × validation`

- **source_conf**: `1.0` for digital text fields; mean Tesseract word confidence for OCR fields.
- **cross_check**: deterministic regex/parser agreement for typed fields like dates, numbers, and ranges.
- **validation**: `1.0` if type and range checks pass; soft penalty otherwise.

`overall_status = needs_review` if any required field confidence is below `FIELD_CONFIDENCE_THRESHOLD`; otherwise `ok`.

## Response shape

`POST /extract` returns:

```json
{
  "schema": {},
  "scores": [
    {
      "name": "patient_id",
      "confidence": 0.92,
      "source": "text",
      "value": "SYN-001"
    }
  ],
  "overall_status": "ok",
  "source": "text"
}
```

## Project layout

```
app/                 FastAPI routes
core/
  ingest.py          PDF path/size validation
  extract_text.py    PyMuPDF text extraction
  classify.py        Digital vs scanned page classification
  preprocess.py      OpenCV preprocessing for OCR
  ocr.py             Tesseract OCR + word confidence
  extract_structured.py Schema-driven LLM extraction
  validate.py        Pydantic validation and coercion
  confidence.py      Per-field confidence scoring
  pipeline.py        End-to-end wiring
  llm/               Provider-agnostic LLM interface
  schema/            Pydantic document schemas
benchmark/           Synthetic dataset generation + runner
tests/               Unit tests
```

## Known limitations

- OCR requires Tesseract to be installed in the runtime environment; Dockerfile installs it, host install is manual.
- LLM extraction uses deterministic stubbed responses in benchmark/test mode; real accuracy depends on provider output quality and prompt tuning.
- Table extraction is stubbed (`NotImplementedError`) in the fast-path and should be completed for table-heavy documents.
- ChromaDB RAG and vision-LLM low-confidence fallback are planned (Phase 7).
- This repo uses synthetic lab reports only. If you adapt it to production, keep real PHI/PII out of the repo.

## License

MIT
