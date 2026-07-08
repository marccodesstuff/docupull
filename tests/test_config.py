import pytest


def test_defaults(monkeypatch):
    from core.config import get_settings
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("TEXT_DENSITY_THRESHOLD", "200")
    s = get_settings()
    assert s.llm_provider == "openai"
    assert s.text_density_threshold == 200
    assert s.ocr_confidence_threshold == 60
    assert s.field_confidence_threshold == 0.75


def test_env_override(monkeypatch):
    from core.config import get_settings
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("TEXT_DENSITY_THRESHOLD", "150")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = get_settings()
    assert s.llm_provider == "anthropic"
    assert s.text_density_threshold == 150
