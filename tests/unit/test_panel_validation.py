from __future__ import annotations

from PIL import Image, ImageDraw

from comic_agent.pipeline.panel_validation import (
    SinglePanelHeuristicValidator,
    apply_retry_strategy,
    get_retry_strategies,
)


def test_single_panel_validator_accepts_plain_single_scene_image():
    image = Image.new("RGB", (512, 512), color="white")

    result = SinglePanelHeuristicValidator().validate(image)

    assert result.decision == "accepted"
    assert result.reason is None


def test_single_panel_validator_rejects_internal_cross_grid():
    image = Image.new("RGB", (512, 512), color="white")
    draw = ImageDraw.Draw(image)
    draw.line((256, 40, 256, 472), fill="black", width=8)
    draw.line((40, 256, 472, 256), fill="black", width=8)

    result = SinglePanelHeuristicValidator().validate(image)

    assert result.decision == "rejected"
    assert "divider lines" in str(result.reason)


def test_single_panel_validator_rejects_light_gutter_cross_grid():
    image = Image.new("RGB", (512, 512), color=(210, 200, 180))
    draw = ImageDraw.Draw(image)
    draw.rectangle((248, 40, 264, 472), fill="white")
    draw.rectangle((40, 248, 472, 264), fill="white")

    result = SinglePanelHeuristicValidator().validate(image)

    assert result.decision == "rejected"
    assert "divider lines" in str(result.reason)


def test_single_panel_validator_rejects_seamless_four_quadrant_layout():
    image = Image.new("RGB", (512, 512), color="white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 255, 255), fill=(235, 210, 180))
    draw.rectangle((256, 0, 511, 255), fill=(180, 220, 245))
    draw.rectangle((0, 256, 255, 511), fill=(190, 230, 180))
    draw.rectangle((256, 256, 511, 511), fill=(240, 200, 210))

    result = SinglePanelHeuristicValidator().validate(image)

    assert result.decision == "rejected"
    assert "seamless multi-panel layout" in str(result.reason)


def test_retry_strategies_are_bounded_and_deterministic():
    strategies = get_retry_strategies()

    assert [strategy.name for strategy in strategies] == [
        "standard",
        "strict_single_scene",
        "minimal_snapshot",
    ]


def test_apply_retry_strategy_appends_suffix_for_stricter_attempt():
    strategies = get_retry_strategies()
    prompt = "Create one full-frame illustration of a single moment."

    rewritten = apply_retry_strategy(prompt, strategies[1])

    assert rewritten.startswith(prompt)
    assert "Retry strategy:" in rewritten
