from __future__ import annotations

from comic_agent.models.comic_request import ComicRequest
from comic_agent.pipeline.story_planner import StoryPlannerAgent, StoryboardAgent, build_story_structure


def test_subject_extraction_prefers_explicit_character(tmp_path):
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        character="戴红围巾的小兔子",
        output_dir=tmp_path,
    )

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.subject == "戴红围巾的小兔子"


def test_subject_extraction_prefers_specific_subject_over_generic(tmp_path):
    request = ComicRequest(
        theme="记录同一只流浪橘猫在四季中的变化，特征保持一致",
        output_dir=tmp_path,
    )

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.subject == "流浪橘猫"


def test_subject_extraction_avoids_action_phrase(tmp_path):
    request = ComicRequest(theme="一只小兔子上学的一天", output_dir=tmp_path)

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.subject == "小兔子"
    assert "上学" not in context.subject


def test_semantic_parser_extracts_activity_object_and_domain_cues(tmp_path):
    request = ComicRequest(theme="机器人修好城市的灯", output_dir=tmp_path)

    context = StoryboardAgent().build_context(request)

    assert context.semantics.subject == "机器人"
    assert context.semantics.activity == "repair"
    assert context.semantics.primary_object == "灯"
    assert context.semantics.setting_hint == "a city street setting"
    assert "problem_solving" in context.semantics.domain_cues


def test_semantic_parser_extracts_lantern_journey_semantics(tmp_path):
    request = ComicRequest(theme="一只狐狸放飞灯笼", output_dir=tmp_path)

    context = StoryboardAgent().build_context(request)

    assert context.semantics.activity == "release a lantern"
    assert context.semantics.primary_object == "灯笼"
    assert "journey" in context.semantics.domain_cues


def test_intent_detection_prefers_seasonal_when_multiple_signals_exist(tmp_path):
    request = ComicRequest(
        theme="记录同一只流浪橘猫在四季中的成长变化",
        output_dir=tmp_path,
    )

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.intent_type == "seasonal_progression"


def test_intent_detection_falls_back_when_no_specific_pattern_exists(tmp_path):
    request = ComicRequest(theme="A fox learns to cook", output_dir=tmp_path)

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.intent_type == "fallback_story"


def test_intent_detection_recognizes_problem_solving_themes(tmp_path):
    request = ComicRequest(theme="机器人修好城市的灯", output_dir=tmp_path)

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.intent_type == "problem_solving"


def test_intent_detection_recognizes_journey_themes(tmp_path):
    request = ComicRequest(theme="一只狐狸放飞灯笼", output_dir=tmp_path)

    planner = StoryboardAgent()
    context = planner.build_context(request)

    assert context.intent_type == "journey_adventure"


def test_school_day_theme_returns_concrete_day_sequence(tmp_path):
    request = ComicRequest(theme="一只小兔子上学的一天", output_dir=tmp_path)

    story = build_story_structure(request)

    assert len(story.panels) == 4
    assert [panel.caption for panel in story.panels] == [
        "Morning",
        "On the Way",
        "At School",
        "Going Home",
    ]
    assert "front door of home" in story.panels[0].scene_description
    assert "taking the first step out to begin school" in story.panels[0].action.lower()
    assert story.panels[0].camera_framing == "medium shot"
    assert "road to school" in story.panels[1].scene_description
    assert "walking toward school with purpose" in story.panels[1].action.lower()
    assert "bright classroom" in story.panels[2].scene_description
    assert "listening and working during class" in story.panels[2].action.lower()
    assert "road home" in story.panels[3].scene_description
    assert "heading home after the school day ends" in story.panels[3].action.lower()
    assert len({panel.scene_description for panel in story.panels}) == 4
    assert all("four-panel layout" not in panel.scene_description for panel in story.panels)
    assert all("encounters the setup" not in panel.scene_description for panel in story.panels)
    assert all("freeze the" in panel.scene_description.lower() or "catch the" in panel.scene_description.lower() for panel in story.panels)


def test_fallback_story_planning_keeps_scenes_distinct(tmp_path):
    request = ComicRequest(theme="一只熊学做饭", output_dir=tmp_path)

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Setup",
        "Complication",
        "Response",
        "Resolution",
    ]
    assert "small kitchen workspace" in story.panels[0].scene_description
    assert "studying the recipe before cooking begins" in story.panels[0].action.lower()
    assert "messy mistake while chopping or mixing" in story.panels[1].action.lower()
    assert "trying again carefully while stirring or adjusting the recipe" in story.panels[2].action.lower()
    assert "serving the completed meal" in story.panels[3].action.lower()
    assert len({panel.scene_description for panel in story.panels}) == 4
    assert all(panel.scene_description != request.theme for panel in story.panels)
    assert all("comic page" not in panel.scene_description for panel in story.panels)


def test_seasonal_theme_assigns_one_season_per_panel(tmp_path):
    request = ComicRequest(
        theme="记录同一只流浪橘猫在四季中的变化，特征保持一致",
        output_dir=tmp_path,
    )

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Spring",
        "Summer",
        "Autumn",
        "Winter",
    ]
    assert "spring alley" in story.panels[0].scene_description
    assert "summer street edge" in story.panels[1].scene_description
    assert "autumn lane" in story.panels[2].scene_description
    assert "winter corner" in story.panels[3].scene_description
    assert all("all seasons" not in panel.scene_description for panel in story.panels)


def test_journey_theme_expands_lantern_story_with_concrete_progression(tmp_path):
    request = ComicRequest(theme="一只狐狸放飞灯笼", output_dir=tmp_path)

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Departure",
        "Encounter",
        "Turning Point",
        "Resolution",
    ]
    assert "dusk courtyard" in story.panels[0].scene_description
    assert "preparing the paper lantern for release" in story.panels[0].action.lower()
    assert "lighting the lantern before release" in story.panels[1].action.lower()
    assert "releasing the lantern into the sky" in story.panels[2].action.lower()
    assert "watching the lantern drift higher after release" in story.panels[3].action.lower()
    assert len({panel.scene_description for panel in story.panels}) == 4


def test_problem_solving_theme_expands_city_light_repair_story(tmp_path):
    request = ComicRequest(theme="机器人修好城市的灯", output_dir=tmp_path)

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Problem",
        "Search",
        "Solution",
        "Payoff",
    ]
    assert "dark city street" in story.panels[0].scene_description
    assert "searching for the cause of the lighting failure" in story.panels[1].action.lower()
    assert "repairing the lighting system" in story.panels[2].action.lower()
    assert "seeing the street come back to life" in story.panels[3].action.lower()
    assert len({panel.scene_description for panel in story.panels}) == 4
    assert all("grid" not in panel.scene_description for panel in story.panels)


def test_problem_solving_theme_for_lost_key_uses_semantic_object(tmp_path):
    request = ComicRequest(theme="小猫找回丢失的钥匙", output_dir=tmp_path)

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Problem",
        "Search",
        "Solution",
        "Payoff",
    ]
    assert "realizing the key is missing" in story.panels[0].action.lower()
    assert "searching under furniture or beside objects for the key" in story.panels[1].action.lower()
    assert "recovering the missing key" in story.panels[2].action.lower()


def test_competition_theme_remains_supported_with_concrete_scenes(tmp_path):
    request = ComicRequest(theme="狐狸参加篮球赛，投进绝杀三分", output_dir=tmp_path)

    story = build_story_structure(request)

    assert [panel.caption for panel in story.panels] == [
        "Opening",
        "Pressure",
        "Climax",
        "Finish",
    ]
    assert "holding the ball before the basketball game reaches its decisive stretch" in story.panels[0].action.lower()
    assert "dribbling near the three-point line" in story.panels[1].action.lower()
    assert "releasing a game-winning three-point shot" in story.panels[2].action.lower()
    assert "ball drop through the hoop" in story.panels[3].action.lower()


def test_build_story_structure_delegates_to_story_planner_agent(tmp_path):
    request = ComicRequest(theme="A fox learns to cook", output_dir=tmp_path)

    story = build_story_structure(request)

    assert len(story.panels) == 4
    assert story.title.startswith("Story sequence:")
    assert all(panel.generated_prompt_base == "" for panel in story.panels)
    assert all(panel.final_image_prompt == "" for panel in story.panels)


def test_story_planner_agent_remains_backward_compatible_alias(tmp_path):
    request = ComicRequest(theme="一只小兔子上学的一天", output_dir=tmp_path)

    story = StoryPlannerAgent().plan(request)

    assert len(story.panels) == 4
    assert story.panels[0].caption == "Morning"
