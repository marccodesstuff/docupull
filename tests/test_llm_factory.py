import pytest

from core.llm.factory import build_client
from core.llm.openai_client import OpenAIClient
from core.llm.anthropic_client import AnthropicClient
from core.schema.lab_report import LabReport


def test_factory_openai_when_env_sets_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    client = build_client()
    assert isinstance(client, OpenAIClient)


def test_factory_anthropic_when_env_sets_anthropic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    client = build_client()
    assert isinstance(client, AnthropicClient)


def test_factory_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "google")
    with pytest.raises(ValueError) as excinfo:
        build_client()
    assert "Unsupported LLM provider" in str(excinfo.value)


def test_base_schema_required_fields():
    assert "patient_id" in LabReport.model_fields
    assert "report_date" in LabReport.model_fields
