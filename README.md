# DocuPull

PDF → validated structured JSON. Handles both text-layer and scanned PDFs with OCR fallback, LLM extraction, and confidence scoring.

## Quick start
```bash
cp .env.example .env
uv sync
uv run pytest
uvicorn app.main:app --reload
```

## Run tests
```bash
PYTHONPATH=. uv run pytest -q
```

## API
- POST /extract – upload a PDF
- GET /health
