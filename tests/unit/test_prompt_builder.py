from __future__ import annotations

from comic_agent.models.comic_request import ComicRequest
from comic_agent.pipeline.prompt_builder import (
    build_character_bible,
    build_style_bible,
    populate_panel_prompts,
)
from comic_agent.pipeline.panel_validation import apply_retry_strategy, get_retry_strategies
from comic_agent.pipeline.safety import SafetyError, reject_unsafe_theme
from comic_agent.pipeline.story_planner import build_story_structure, plan_story


def test_prompt_builder_includes_shared_bibles_and_four_panels(tmp_path):
    request = ComicRequest(
        theme="A fox learns to cook",
        style="watercolor",
        character="orange fox with apron",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    character_bible = build_character_bible(request)
    style_bible = build_style_bible(request)
    story, warnings = populate_panel_prompts(story, request, character_bible, style_bible)

    assert len(story.panels) == 4
    assert warnings == []
    for panel in story.panels:
        assert "Draw exactly one finished panel image." in panel.final_image_prompt
        assert "This prompt describes one panel only." in panel.final_image_prompt
        assert "Do not draw a full comic page, extra panels" in panel.final_image_prompt
        assert "The main subject is orange fox with apron." in panel.final_image_prompt
        assert "Give the subject" in panel.final_image_prompt
        assert "Render it as watercolor." in panel.final_image_prompt
        assert "Show only one continuous scene in one undivided image." in panel.final_image_prompt
        assert "Freeze one exact instant instead of showing a sequence of events." in panel.final_image_prompt
        assert "Keep the subject in one location and do not repeat the subject in multiple places within the image." in panel.final_image_prompt
        assert "Hard constraints: single full-frame illustration; one scene only;" in panel.final_image_prompt
        assert "no collage" in panel.final_image_prompt
        assert "four-panel visual language" not in panel.final_image_prompt
        assert "comic style" not in panel.final_image_prompt
        assert "panel 1" not in panel.final_image_prompt
        assert "four panels" not in panel.final_image_prompt
        assert panel.prompt_source == "generated"


def test_prompt_builder_merges_global_and_panel_guidance(tmp_path):
    request = ComicRequest(
        theme="A turtle joins a race",
        image_prompt="sunset lighting and fixed comic readability",
        panel_prompts={2: "heroic close-up"},
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    story, warnings = populate_panel_prompts(
        story,
        request,
        build_character_bible(request),
        build_style_bible(request),
    )

    assert story.panels[0].prompt_source == "merged"
    assert "Additional guidance: sunset lighting." in story.panels[0].final_image_prompt
    assert "fixed comic readability" not in story.panels[0].final_image_prompt
    assert story.panels[1].prompt_source == "user_guided"
    assert "Panel-specific guidance: heroic close-up." in story.panels[1].final_image_prompt
    assert warnings == []


def test_prompt_builder_rewrites_unsafe_guidance(tmp_path):
    request = ComicRequest(
        theme="A rabbit paints a mural",
        image_prompt="gore background",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    story, warnings = populate_panel_prompts(
        story,
        request,
        build_character_bible(request),
        build_style_bible(request),
    )

    assert "[removed unsafe content]" in story.panels[0].final_image_prompt
    assert any("unsafe content" in warning for warning in warnings)


def test_unsafe_theme_is_rejected():
    try:
        reject_unsafe_theme("gore scene in a classroom")
    except SafetyError as exc:
        assert "Unsafe theme input detected" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected unsafe theme rejection")


def test_four_season_theme_stays_single_scene_per_panel(tmp_path):
    request = ComicRequest(
        theme="记录同一只流浪橘猫在四季中的变化，特征保持一致",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    character_bible = build_character_bible(request)
    style_bible = build_style_bible(request)
    story, warnings = populate_panel_prompts(story, request, character_bible, style_bible)

    assert warnings == []
    assert character_bible.summary == "流浪橘猫"
    assert "orange tabby coat with visible stripes" in character_bible.appearance_traits
    assert "slightly scruffy fur and alert street-cat posture" in character_bible.appearance_traits
    assert "spring alley" in story.panels[0].scene_description
    assert "summer street edge" in story.panels[1].scene_description
    assert "autumn lane" in story.panels[2].scene_description
    assert "winter corner" in story.panels[3].scene_description
    for panel in story.panels:
        assert "single full-frame illustration" in panel.final_image_prompt
        assert "one subject occurrence unless another character is explicitly described" in panel.final_image_prompt
        assert "one location only" in panel.final_image_prompt
        assert "no comparison sheet" in panel.final_image_prompt
        assert "fixed comic readability" not in panel.final_image_prompt
        assert "panel-to-panel continuity" not in panel.final_image_prompt
        assert "four-panel visual language" not in panel.final_image_prompt
        assert "four panels" not in panel.final_image_prompt
        assert "comic style" not in panel.final_image_prompt


def test_prompt_builder_avoids_multi_panel_language_in_provider_prompt(tmp_path):
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    story, _ = populate_panel_prompts(
        story,
        request,
        build_character_bible(request),
        build_style_bible(request),
    )

    first_prompt = story.panels[0].final_image_prompt
    assert "只画一张完整单格插画。" in first_prompt
    assert "这条提示只描述当前这一格，不要画整页漫画、额外分格、多个连续场景" in first_prompt
    assert "当前这一格的场景是：" in first_prompt
    assert "镜头类型固定为：medium shot。" in first_prompt
    assert "The main subject is 小兔子." in first_prompt
    assert "Show only the opening moment, not the whole story." in first_prompt
    assert "Do not summarize later events from the story in this image." in first_prompt
    assert "panel 1" not in first_prompt
    assert "default comic style" not in first_prompt
    assert "across all four panels" not in first_prompt
    assert "Four-panel comic" not in first_prompt
    assert "every other panel" not in first_prompt
    assert "Show only one continuous scene in one undivided image." in first_prompt
    assert "Freeze one exact instant instead of showing a sequence of events." in first_prompt
    assert "one undivided image" in first_prompt
    assert "freeze one exact instant" in first_prompt
    assert "no before-and-after sequence" in first_prompt
    assert "do not split the image into sections" in first_prompt
    assert "do not draw multiple frames or multiple scenes in one image" in first_prompt
    assert "Use medium shot framing." in first_prompt


def test_prompt_builder_uses_story_subject_for_bear_theme(tmp_path):
    request = ComicRequest(
        theme="一只熊学做饭",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    character_bible = build_character_bible(request)
    story, warnings = populate_panel_prompts(
        story,
        request,
        character_bible,
        build_style_bible(request),
    )

    assert warnings == []
    assert character_bible.summary == "熊"
    assert "broad body, rounded ears, and sturdy paws" in character_bible.appearance_traits
    assert "The main subject is 熊." in story.panels[0].final_image_prompt


def test_prompt_builder_supports_storyboard_expanded_lantern_story(tmp_path):
    request = ComicRequest(
        theme="一只狐狸放飞灯笼",
        output_dir=tmp_path,
    )
    story = build_story_structure(request)
    story, warnings = populate_panel_prompts(
        story,
        request,
        build_character_bible(request),
        build_style_bible(request),
    )

    assert warnings == []
    assert story.panels[0].caption == "Departure"
    assert "preparing the paper lantern for release" in story.panels[0].action.lower()
    assert "lighting the lantern before release" in story.panels[1].action.lower()
    assert "releasing the lantern into the sky" in story.panels[2].action.lower()
    assert "watching the lantern drift higher after release" in story.panels[3].action.lower()
    assert "four-panel layout" not in story.panels[0].final_image_prompt
    assert "comic page" not in story.panels[0].final_image_prompt


def test_prompt_builder_supports_lm_assisted_story_subject(monkeypatch, tmp_path):
    monkeypatch.setenv("COMIC_AGENT_LM_API_URL", "https://example.com/v1/chat/completions")
    monkeypatch.setenv("COMIC_AGENT_LM_API_KEY", "test-key")
    monkeypatch.setenv("COMIC_AGENT_LM_MODEL", "test-model")
    lm_payload = """
    {
      "subject": "熊",
      "panels": [
        {
          "caption": "Setup",
          "dialogue": "熊 reads the recipe.",
          "scene_description": "熊 stands in a small kitchen studying a recipe beside bowls and ingredients.",
          "action": "Study the recipe before cooking begins.",
          "emotion": "curious",
          "camera_framing": "medium shot",
          "visual_description": "Show one recipe, one kitchen counter, and one starting moment."
        },
        {
          "caption": "Complication",
          "dialogue": "熊 makes a messy mistake.",
          "scene_description": "熊 makes a messy mistake while chopping or mixing ingredients at the counter.",
          "action": "Make a messy mistake while cooking.",
          "emotion": "tense",
          "camera_framing": "medium shot",
          "visual_description": "Show spilled ingredients and one immediate problem."
        },
        {
          "caption": "Response",
          "dialogue": "熊 tries again carefully.",
          "scene_description": "熊 tries again carefully while stirring a pan and checking the recipe.",
          "action": "Try again carefully at the stove.",
          "emotion": "determined",
          "camera_framing": "close-up",
          "visual_description": "Show one pan, one utensil, and one focused correction moment."
        },
        {
          "caption": "Resolution",
          "dialogue": "熊 serves the finished meal.",
          "scene_description": "熊 serves the finished meal on the table with visible pride.",
          "action": "Serve the completed meal.",
          "emotion": "joyful",
          "camera_framing": "wide shot",
          "visual_description": "Show one plated dish and one satisfied ending moment."
        }
      ]
    }
    """.strip()
    monkeypatch.setattr(
        "comic_agent.pipeline.story_planner.LMStoryPlanner._request_payload",
        lambda self, request: lm_payload,
    )
    request = ComicRequest(
        theme="一只熊学做饭",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    story, planner_run = plan_story(request)
    character_bible = build_character_bible(request, subject_override=story.subject)
    story, warnings = populate_panel_prompts(story, request, character_bible, build_style_bible(request))

    assert planner_run.actual_mode == "lm_assisted"
    assert warnings == []
    assert character_bible.summary == "熊"
    assert "The main subject is 熊." in story.panels[0].final_image_prompt


def test_retry_strategy_can_strengthen_provider_facing_prompt(tmp_path):
    request = ComicRequest(theme="一只小兔子上学的一天", output_dir=tmp_path)
    story = build_story_structure(request)
    story, _ = populate_panel_prompts(
        story,
        request,
        build_character_bible(request),
        build_style_bible(request),
    )

    strategies = get_retry_strategies()
    rewritten = apply_retry_strategy(story.panels[0].final_image_prompt, strategies[1])

    assert rewritten.startswith(story.panels[0].final_image_prompt)
    assert "Retry strategy:" in rewritten
