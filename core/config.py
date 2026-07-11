from __future__ import annotations

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-haiku-latest"
    tesseract_cmd: str | None = None
    text_density_threshold: int = 200
    ocr_confidence_threshold: int = 60
    field_confidence_threshold: float = 0.75
    debug: bool = False
    log_level: str = "INFO"
    upload_dir: str = "./tmp/uploads"
    output_dir: str = "./tmp/outputs"


def get_settings():
    return Settings()


__all__ = ["Settings", "get_settings"]
