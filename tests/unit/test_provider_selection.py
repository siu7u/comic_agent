from __future__ import annotations

import json

import pytest
from PIL import Image

import comic_agent.cli.generate as generate_module
from comic_agent.models.comic_request import ComicRequest
from comic_agent.pipeline.panel_validation import SinglePanelValidationResult
from comic_agent.providers.base import ProviderConfigurationError, ProviderGenerationError
from comic_agent.providers.mock import MockImageProvider


class FakeRealProvider:
    name = "FakeRealProvider"
    mode = "real"

    def validate_configuration(self) -> None:
        return None

    def generate_panel_image(self, panel):
        return Image.new("RGB", (512, 512), color="navy")


class FailingRealProvider:
    name = "FailingRealProvider"
    mode = "real"

    def validate_configuration(self) -> None:
        return None

    def generate_panel_image(self, panel):
        raise ProviderGenerationError("simulated provider failure")


def test_build_provider_returns_mock_by_default():
    provider = generate_module.build_provider("mock")

    assert isinstance(provider, MockImageProvider)
    assert provider.mode == "mock"


def test_parse_request_defaults_output_to_timestamped_directory_under_output(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("COMIC_AGENT_LM_ENABLED", raising=False)

    args = generate_module.build_parser().parse_args(["generate", "--theme", "A snail opens a cafe"])

    request = generate_module.parse_request(args)

    assert request.provider == "wanx"
    assert request.planner_mode is None
    assert request.output_dir.parent == tmp_path / "output"
    assert request.output_dir.name.startswith("comic-output-")


def test_parse_request_defaults_to_lm_assisted_when_env_is_unset(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("COMIC_AGENT_LM_ENABLED", raising=False)

    args = generate_module.build_parser().parse_args(["generate", "--theme", "A snail opens a cafe"])

    request = generate_module.parse_request(args)

    assert generate_module.plan_story(request)[1].requested_mode == "lm_assisted"


def test_parse_request_defaults_to_rule_based_when_lm_is_disabled_by_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COMIC_AGENT_LM_ENABLED", "off")

    args = generate_module.build_parser().parse_args(["generate", "--theme", "A snail opens a cafe"])

    request = generate_module.parse_request(args)

    assert generate_module.plan_story(request)[1].requested_mode == "rule_based"


def test_parse_request_accepts_explicit_lm_assisted_planner(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    args = generate_module.build_parser().parse_args(
        ["generate", "--theme", "A snail opens a cafe", "--planner", "lm_assisted"]
    )

    request = generate_module.parse_request(args)

    assert request.planner_mode == "lm_assisted"


def test_run_generation_with_real_provider_records_provider_details(tmp_path, monkeypatch):
    monkeypatch.setitem(generate_module.PROVIDER_FACTORIES, "wanx", FakeRealProvider)
    request = ComicRequest(theme="A crow paints a mural", provider="wanx", output_dir=tmp_path)

    metadata = generate_module.run_generation(request)

    assert metadata.provider == "FakeRealProvider"
    assert metadata.provider_mode == "real"
    assert metadata.provider_run.completed_successfully is True
    assert all(panel.provider_mode == "real" for panel in metadata.story.panels)


def test_main_reports_missing_real_provider_configuration(tmp_path, capsys):
    code = generate_module.main(["generate", "--theme", "A mole builds a tunnel", "--provider", "wanx", "--out", str(tmp_path)])

    captured = capsys.readouterr()
    assert code == 1
    assert "Missing environment variables" in captured.out


def test_real_provider_failure_retries_and_writes_metadata(tmp_path, monkeypatch):
    monkeypatch.setitem(generate_module.PROVIDER_FACTORIES, "wanx", FailingRealProvider)
    request = ComicRequest(theme="A raccoon opens a bakery", provider="wanx", output_dir=tmp_path)

    with pytest.raises(ProviderGenerationError, match="Image generation failed for panel 1"):
        generate_module.run_generation(request)

    payload = json.loads((tmp_path / "metadata.json").read_text(encoding="utf-8"))
    assert payload["provider"] == "FailingRealProvider"
    assert payload["provider_mode"] == "real"
    assert payload["provider_run"]["completed_successfully"] is False
    assert payload["story"]["panels"][0]["retry_count"] == 2
    assert payload["story"]["panels"][0]["failure_message"] == "simulated provider failure"


def test_run_generation_rejects_provider_successful_but_validator_failed_panel(tmp_path, monkeypatch):
    monkeypatch.setitem(generate_module.PROVIDER_FACTORIES, "wanx", FakeRealProvider)

    decisions = [
        SinglePanelValidationResult(decision="rejected", reason="detected divider lines"),
        SinglePanelValidationResult(decision="rejected", reason="detected divider lines"),
        SinglePanelValidationResult(decision="rejected", reason="detected divider lines"),
    ]

    class StubValidator:
        def validate(self, image):
            return decisions.pop(0)

    monkeypatch.setattr(generate_module, "SinglePanelHeuristicValidator", lambda: StubValidator())
    request = ComicRequest(theme="A crow paints a mural", provider="wanx", output_dir=tmp_path)

    with pytest.raises(ProviderGenerationError, match="detected divider lines"):
        generate_module.run_generation(request)

    payload = json.loads((tmp_path / "metadata.json").read_text(encoding="utf-8"))
    assert payload["panel_attempt_traces"][0]["final_status"] == "failed_validation"
    assert len(payload["panel_attempt_traces"][0]["attempts"]) == 3
    assert payload["panel_attempt_traces"][0]["attempts"][0]["validation_decision"] == "rejected"


def test_run_generation_retries_after_validator_rejection_and_accepts_later_attempt(tmp_path, monkeypatch):
    monkeypatch.setitem(generate_module.PROVIDER_FACTORIES, "wanx", FakeRealProvider)

    decisions = [
        SinglePanelValidationResult(decision="rejected", reason="detected divider lines"),
        SinglePanelValidationResult(decision="accepted"),
        SinglePanelValidationResult(decision="accepted"),
        SinglePanelValidationResult(decision="accepted"),
        SinglePanelValidationResult(decision="accepted"),
    ]

    class StubValidator:
        def validate(self, image):
            return decisions.pop(0)

    monkeypatch.setattr(generate_module, "SinglePanelHeuristicValidator", lambda: StubValidator())
    request = ComicRequest(theme="A crow paints a mural", provider="wanx", output_dir=tmp_path)

    metadata = generate_module.run_generation(request)

    assert metadata.story.panels[0].accepted_attempt_number == 2
    assert metadata.panel_attempt_traces[0].accepted_attempt_number == 2
    assert metadata.panel_attempt_traces[0].attempts[0]["strategy_name"] == "standard"
    assert metadata.panel_attempt_traces[0].attempts[1]["strategy_name"] == "strict_single_scene"
