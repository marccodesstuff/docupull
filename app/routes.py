from pathlib import Path

from core.pipeline import run
from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

router = APIRouter()
FILE_DEPENDENCY = File(...)


@router.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@router.post("/extract")
async def extract(file: UploadFile = FILE_DEPENDENCY) -> dict:
    import os
    import tempfile
    from contextlib import suppress

    from docupull.config import get_settings

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.pdf").suffix
    if suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=str(upload_dir))
    try:
        content = await file.read()
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        return run(tmp_path)
    finally:
        with suppress(OSError):
            os.remove(tmp_path)
