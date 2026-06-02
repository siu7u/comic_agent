from __future__ import annotations

import json

from PIL import Image

import comic_agent.cli.generate as generate_module
from comic_agent.pipeline.panel_validation import SinglePanelValidationResult


def test_mock_pipeline_creates_expected_outputs(tmp_path):
    out_dir = tmp_path / "comic"

    code = generate_module.main(
        ["generate", "--theme", "A shy cat learns to skateboard", "--planner", "rule_based", "--provider", "mock", "--out", str(out_dir)]
    )

    assert code == 0
    for index in range(1, 5):
        assert (out_dir / f"panel-{index}.png").exists()
    assert (out_dir / "comic.png").exists()
    assert (out_dir / "metadata.json").exists()
    assert Image.open(out_dir / "comic.png").size == (1054, 1054)
    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert payload["provider"] == "MockImageProvider"
    assert payload["provider_mode"] == "mock"
    assert payload["planner_run"]["requested_mode"] == "rule_based"
    assert payload["planner_run"]["actual_mode"] == "rule_based"
    assert payload["panel_attempt_traces"][0]["final_status"] == "accepted"
    assert payload["panel_attempt_traces"][0]["attempts"][0]["validation_decision"] == "accepted"
    assert len({panel["scene_description"] for panel in payload["story"]["panels"]}) == 4


def test_mock_pipeline_records_guidance_and_reference_metadata(tmp_path):
    out_dir = tmp_path / "guided"
    reference = tmp_path / "reference.png"
    Image.new("RGB", (16, 16), color="purple").save(reference)

    code = generate_module.main(
        [
            "generate",
            "--theme",
            "A frog builds a kite",
            "--planner",
            "rule_based",
            "--provider",
            "mock",
            "--image-prompt",
            "misty dawn",
            "--panel-prompt-2",
            "dramatic close-up",
            "--reference-image",
            str(reference),
            "--out",
            str(out_dir),
        ]
    )

    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))

    assert code == 0
    assert payload["reference_image_path"] == str(reference)
    assert payload["provider"] == "MockImageProvider"
    assert payload["provider_mode"] == "mock"
    assert payload["story"]["panels"][0]["prompt_source"] == "merged"
    assert payload["story"]["panels"][1]["prompt_source"] == "user_guided"


def test_mock_pipeline_rejects_unsafe_theme(tmp_path, capsys):
    out_dir = tmp_path / "rejected"

    code = generate_module.main(
        ["generate", "--theme", "gore classroom", "--planner", "rule_based", "--provider", "mock", "--out", str(out_dir)]
    )

    captured = capsys.readouterr()
    assert code == 1
    assert "Unsafe theme input detected" in captured.out
    assert not out_dir.exists()


def test_pipeline_supports_real_provider_selection_with_stub(tmp_path, monkeypatch):
    out_dir = tmp_path / "real"

    class StubRealProvider:
        name = "StubRealProvider"
        mode = "real"

        def validate_configuration(self) -> None:
            return None

        def generate_panel_image(self, panel):
            return Image.new("RGB", (512, 512), color="orange")

    monkeypatch.setitem(generate_module.PROVIDER_FACTORIES, "wanx", StubRealProvider)

    code = generate_module.main(
        ["generate", "--theme", "A fox launches a lantern", "--planner", "rule_based", "--provider", "wanx", "--out", str(out_dir)]
    )

    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert code == 0
    assert payload["provider"] == "StubRealProvider"
    assert payload["provider_mode"] == "real"
    assert payload["provider_run"]["completed_successfully"] is True


def test_mock_pipeline_supports_lm_assisted_planner_with_stubbed_story(monkeypatch, tmp_path):
    out_dir = tmp_path / "lm"
    monkeypatch.setenv("COMIC_AGENT_LM_API_URL", "https://example.com/v1/chat/completions")
    monkeypatch.setenv("COMIC_AGENT_LM_API_KEY", "test-key")
    monkeypatch.setenv("COMIC_AGENT_LM_MODEL", "test-model")
    monkeypatch.setattr(
        "comic_agent.pipeline.story_planner.LMStoryPlanner._request_payload",
        lambda self, request: json.dumps(
            {
                "subject": "小兔子",
                "panels": [
                    {
                        "caption": "Morning",
                        "dialogue": "小兔子 checks the morning plan.",
                        "scene_description": "小兔子 stands at the front door with a school bag in clear morning light.",
                        "action": "Take the first step out toward school.",
                        "emotion": "eager",
                        "camera_framing": "medium shot",
                        "visual_description": "Show one doorway, one school bag, and one departure moment.",
                    },
                    {
                        "caption": "On the Way",
                        "dialogue": "小兔子 keeps moving forward.",
                        "scene_description": "小兔子 walks along the road to school with early light on the path.",
                        "action": "Walk steadily toward school.",
                        "emotion": "focused",
                        "camera_framing": "medium shot",
                        "visual_description": "Show one road, one walking stride, and one travel moment.",
                    },
                    {
                        "caption": "At School",
                        "dialogue": "小兔子 listens carefully in class.",
                        "scene_description": "小兔子 sits in a bright classroom with books and pencils on the desk.",
                        "action": "Focus on the lesson in class.",
                        "emotion": "engaged",
                        "camera_framing": "medium shot",
                        "visual_description": "Show one desk, one classroom activity, and one attentive moment.",
                    },
                    {
                        "caption": "Going Home",
                        "dialogue": "小兔子 feels good after school.",
                        "scene_description": "小兔子 walks home with the school bag in warm evening light.",
                        "action": "Head home after the school day ends.",
                        "emotion": "relieved",
                        "camera_framing": "wide shot",
                        "visual_description": "Show one road home, one school bag, and one return moment.",
                    },
                ],
            },
            ensure_ascii=False,
        ),
    )

    code = generate_module.main(
        [
            "generate",
            "--theme",
            "一只小兔子上学的一天",
            "--planner",
            "lm_assisted",
            "--provider",
            "mock",
            "--out",
            str(out_dir),
        ]
    )

    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert code == 0
    assert payload["planner_run"]["requested_mode"] == "lm_assisted"
    assert payload["planner_run"]["actual_mode"] == "lm_assisted"
    assert payload["story"]["subject"] == "小兔子"


def test_mock_pipeline_records_retry_trace_when_validator_rejects_first_attempt(monkeypatch, tmp_path):
    out_dir = tmp_path / "retry"

    decisions = iter(
        [
            ("rejected", "detected divider lines"),
            ("accepted", None),
            ("accepted", None),
            ("accepted", None),
            ("accepted", None),
        ]
    )

    class StubValidator:
        def validate(self, image):
            decision, reason = next(decisions)
            return SinglePanelValidationResult(decision=decision, reason=reason)

    monkeypatch.setattr(generate_module, "SinglePanelHeuristicValidator", lambda: StubValidator())

    code = generate_module.main(
        [
            "generate",
            "--theme",
            "A shy cat learns to skateboard",
            "--planner",
            "rule_based",
            "--provider",
            "mock",
            "--out",
            str(out_dir),
        ]
    )

    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert code == 0
    assert payload["panel_attempt_traces"][0]["accepted_attempt_number"] == 2
    assert payload["panel_attempt_traces"][0]["attempts"][0]["validation_decision"] == "rejected"
    assert payload["panel_attempt_traces"][0]["attempts"][1]["strategy_name"] == "strict_single_scene"


def test_mock_pipeline_preserves_storyboard_agent_output_shape_for_school_day_theme(tmp_path):
    out_dir = tmp_path / "school-day"

    code = generate_module.main(
        [
            "generate",
            "--theme",
            "一只小兔子上学的一天",
            "--provider",
            "mock",
            "--out",
            str(out_dir),
        ]
    )

    payload = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert code == 0
    assert [panel["caption"] for panel in payload["story"]["panels"]] == [
        "Morning",
        "On the Way",
        "At School",
        "Going Home",
    ]
    assert "front door" in payload["story"]["panels"][0]["scene_description"]
    assert "classroom" in payload["story"]["panels"][2]["scene_description"]
