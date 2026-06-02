from __future__ import annotations

import json

from comic_agent.models.bibles import CharacterBible, StyleBible
from comic_agent.models.comic_request import ComicRequest
from comic_agent.models.metadata import MetadataRecord, PanelAttemptTraceRecord, PlannerRunRecord, ProviderRunRecord
from comic_agent.models.panel import PanelSpec, StoryStructure
from comic_agent.pipeline.exporter import write_metadata


def test_metadata_export_records_warnings_and_retry_counts(tmp_path):
    request = ComicRequest(theme="A bat writes poetry", output_dir=tmp_path)
    panel = PanelSpec(
        index=1,
        caption="Setup",
        dialogue="Hello",
        scene_description="Scene",
        action="Act",
        emotion="Calm",
        camera_framing="wide shot",
        visual_description="Visual",
        generated_prompt_base="base",
        final_image_prompt="final",
        prompt_source="merged",
        warnings=["panel warning"],
        retry_count=2,
        input_mode="text_only",
    )
    record = MetadataRecord(
        request=request,
        character_bible=CharacterBible(summary="bat"),
        style_bible=StyleBible(style_name="ink", tone="calm"),
        story=StoryStructure(title="title", premise="premise", panels=[panel]),
        planner_run=PlannerRunRecord(requested_mode="rule_based", actual_mode="rule_based"),
        provider="MockImageProvider",
        provider_mode="mock",
        provider_run=ProviderRunRecord(
            provider_name="MockImageProvider",
            provider_mode="mock",
            started_with_valid_config=True,
            completed_successfully=True,
        ),
        reference_image_path=None,
        panel_image_paths=["panel-1.png"],
        final_comic_path="comic.png",
        warnings=["request warning"],
    )

    metadata_path = write_metadata(tmp_path, record)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert payload["warnings"] == ["request warning"]
    assert payload["story"]["panels"][0]["retry_count"] == 2
    assert payload["story"]["panels"][0]["warnings"] == ["panel warning"]
    assert payload["provider"] == "MockImageProvider"
    assert payload["provider_mode"] == "mock"
    assert payload["provider_run"]["completed_successfully"] is True
    assert payload["planner_run"]["requested_mode"] == "rule_based"
    assert payload["planner_run"]["actual_mode"] == "rule_based"
    assert payload["panel_attempt_traces"] == []


def test_metadata_export_records_provider_failure_details(tmp_path):
    request = ComicRequest(theme="A bear repairs a radio", provider="wanx", output_dir=tmp_path)
    panel = PanelSpec(
        index=1,
        caption="Setup",
        dialogue="Hello",
        scene_description="Scene",
        action="Act",
        emotion="Calm",
        camera_framing="wide shot",
        visual_description="Visual",
        generated_prompt_base="base",
        final_image_prompt="final",
        prompt_source="generated",
        retry_count=2,
        input_mode="text_only",
        provider_name="WanxImageProvider",
        provider_mode="real",
        generation_succeeded=False,
        failure_message="provider failed",
    )
    record = MetadataRecord(
        request=request,
        character_bible=CharacterBible(summary="bear"),
        style_bible=StyleBible(style_name="ink", tone="calm"),
        story=StoryStructure(title="title", premise="premise", panels=[panel]),
        planner_run=PlannerRunRecord(
            requested_mode="lm_assisted",
            actual_mode="rule_based",
            fallback_triggered=True,
            fallback_reason="LM-assisted planning returned invalid JSON",
        ),
        provider="WanxImageProvider",
        provider_mode="real",
        provider_run=ProviderRunRecord(
            provider_name="WanxImageProvider",
            provider_mode="real",
            started_with_valid_config=True,
            completed_successfully=False,
            failure_message="Image generation failed for panel 1",
        ),
        reference_image_path=None,
        panel_image_paths=[],
        final_comic_path="",
        warnings=[],
    )

    metadata_path = write_metadata(tmp_path, record)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert payload["provider"] == "WanxImageProvider"
    assert payload["provider_mode"] == "real"
    assert payload["provider_run"]["completed_successfully"] is False
    assert payload["provider_run"]["failure_message"] == "Image generation failed for panel 1"
    assert payload["story"]["panels"][0]["failure_message"] == "provider failed"
    assert payload["planner_run"]["requested_mode"] == "lm_assisted"
    assert payload["planner_run"]["actual_mode"] == "rule_based"
    assert payload["planner_run"]["fallback_triggered"] is True
    assert "invalid JSON" in payload["planner_run"]["fallback_reason"]
    assert payload["panel_attempt_traces"] == []


def test_metadata_export_records_panel_attempt_traces(tmp_path):
    request = ComicRequest(theme="A fox learns to cook", output_dir=tmp_path)
    panel = PanelSpec(
        index=1,
        caption="Setup",
        dialogue="Hello",
        scene_description="Scene",
        action="Act",
        emotion="Calm",
        camera_framing="wide shot",
        visual_description="Visual",
        generated_prompt_base="base",
        final_image_prompt="final",
        prompt_source="generated",
        retry_count=1,
        input_mode="text_only",
        accepted_attempt_number=2,
        validation_status="accepted",
    )
    record = MetadataRecord(
        request=request,
        character_bible=CharacterBible(summary="fox"),
        style_bible=StyleBible(style_name="ink", tone="calm"),
        story=StoryStructure(title="title", premise="premise", panels=[panel]),
        planner_run=PlannerRunRecord(requested_mode="rule_based", actual_mode="rule_based"),
        provider="MockImageProvider",
        provider_mode="mock",
        provider_run=ProviderRunRecord(
            provider_name="MockImageProvider",
            provider_mode="mock",
            started_with_valid_config=True,
            completed_successfully=True,
        ),
        reference_image_path=None,
        panel_image_paths=["panel-1.png"],
        final_comic_path="comic.png",
        panel_attempt_traces=[
            PanelAttemptTraceRecord(
                panel_index=1,
                final_status="accepted",
                attempts=[
                    {
                        "attempt_number": 1,
                        "strategy_name": "standard",
                        "generated_image_available": True,
                        "validation_decision": "rejected",
                        "validation_reason": "detected divider lines",
                    },
                    {
                        "attempt_number": 2,
                        "strategy_name": "strict_single_scene",
                        "generated_image_available": True,
                        "validation_decision": "accepted",
                        "validation_reason": None,
                    },
                ],
                accepted_attempt_number=2,
            )
        ],
    )

    metadata_path = write_metadata(tmp_path, record)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert payload["panel_attempt_traces"][0]["final_status"] == "accepted"
    assert payload["panel_attempt_traces"][0]["accepted_attempt_number"] == 2
    assert payload["panel_attempt_traces"][0]["attempts"][0]["validation_decision"] == "rejected"
    assert payload["panel_attempt_traces"][0]["attempts"][1]["strategy_name"] == "strict_single_scene"
