from __future__ import annotations

import json

from comic_agent.models.comic_request import ComicRequest
from comic_agent.pipeline import story_planner


def _set_lm_env(monkeypatch) -> None:
    monkeypatch.setenv("COMIC_AGENT_LM_API_URL", "https://example.com/v1/chat/completions")
    monkeypatch.setenv("COMIC_AGENT_LM_API_KEY", "test-key")
    monkeypatch.setenv("COMIC_AGENT_LM_MODEL", "test-model")


def _valid_lm_payload(subject: str = "小兔子") -> str:
    return json.dumps(
        {
            "subject": subject,
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
    )


def test_planner_mode_defaults_to_lm_assisted_when_env_is_unset(monkeypatch):
    monkeypatch.delenv("COMIC_AGENT_LM_ENABLED", raising=False)

    assert story_planner.normalize_planner_mode(None) == "lm_assisted"


def test_planner_mode_uses_rule_based_when_lm_is_disabled_by_env(monkeypatch):
    monkeypatch.setenv("COMIC_AGENT_LM_ENABLED", "false")

    assert story_planner.normalize_planner_mode(None) == "rule_based"


def test_validate_lm_storyboard_payload_accepts_strict_json(tmp_path):
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    story = story_planner.validate_lm_storyboard_payload(_valid_lm_payload(), request)

    assert story.subject == "小兔子"
    assert [panel.caption for panel in story.panels] == ["Morning", "On the Way", "At School", "Going Home"]
    assert "front door" in story.panels[0].scene_description


def test_validate_lm_storyboard_payload_normalizes_camera_framing_aliases(tmp_path):
    request = ComicRequest(
        theme="主角立志减肥，第一格运动，第二格流汗，第三格奖励自己，第四格吃火锅。",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )
    payload = json.loads(_valid_lm_payload())
    payload["panels"][0]["camera_framing"] = "中景，正面视角"
    payload["panels"][1]["camera_framing"] = "特写镜头，聚焦脸上汗水"
    payload["panels"][2]["camera_framing"] = "俯拍"
    payload["panels"][3]["camera_framing"] = "宽镜头，展现丰盛的火锅和享受的小胖"

    story = story_planner.validate_lm_storyboard_payload(json.dumps(payload, ensure_ascii=False), request)

    assert story.panels[0].camera_framing == "medium shot"
    assert story.panels[1].camera_framing == "close-up"
    assert story.panels[2].camera_framing == "overhead shot"
    assert story.panels[3].camera_framing == "wide shot"


def test_build_lm_prompt_requires_chinese_and_non_placeholder_subject(tmp_path):
    request = ComicRequest(
        theme="主角获得超能力，却只用来多睡五分钟。",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )

    prompt = story_planner._build_lm_prompt(request)

    assert "Write every field value in Chinese." in prompt
    assert "Do not use placeholder subjects such as Protagonist" in prompt
    assert "Do not invent how the power was obtained" in prompt


def test_plan_story_uses_lm_assisted_result_when_enabled(monkeypatch, tmp_path):
    _set_lm_env(monkeypatch)
    monkeypatch.setattr(story_planner.LMStoryPlanner, "_request_payload", lambda self, request: _valid_lm_payload())
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    story, planner_run = story_planner.plan_story(request)

    assert planner_run.requested_mode == "lm_assisted"
    assert planner_run.actual_mode == "lm_assisted"
    assert planner_run.fallback_triggered is False
    assert story.subject == "小兔子"
    assert [panel.caption for panel in story.panels] == ["Morning", "On the Way", "At School", "Going Home"]


def test_plan_story_falls_back_on_malformed_json(monkeypatch, tmp_path):
    _set_lm_env(monkeypatch)
    monkeypatch.setattr(story_planner.LMStoryPlanner, "_request_payload", lambda self, request: "{")
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    story, planner_run = story_planner.plan_story(request)

    assert planner_run.actual_mode == "rule_based"
    assert planner_run.fallback_triggered is True
    assert "invalid JSON" in planner_run.fallback_reason
    assert [panel.caption for panel in story.panels] == ["Morning", "On the Way", "At School", "Going Home"]


def test_plan_story_falls_back_on_invalid_storyboard_shape(monkeypatch, tmp_path):
    _set_lm_env(monkeypatch)
    invalid_payload = json.dumps({"subject": "小兔子", "panels": [{"caption": "Only one"}]}, ensure_ascii=False)
    monkeypatch.setattr(story_planner.LMStoryPlanner, "_request_payload", lambda self, request: invalid_payload)
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    _, planner_run = story_planner.plan_story(request)

    assert planner_run.actual_mode == "rule_based"
    assert "missing required field" in planner_run.fallback_reason


def test_plan_story_falls_back_when_lm_times_out(monkeypatch, tmp_path):
    _set_lm_env(monkeypatch)

    def raise_timeout(self, request):
        raise TimeoutError("timed out")

    monkeypatch.setattr(story_planner.LMStoryPlanner, "_request_payload", raise_timeout)
    request = ComicRequest(
        theme="A fox learns to cook",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    story, planner_run = story_planner.plan_story(request)

    assert planner_run.actual_mode == "rule_based"
    assert planner_run.fallback_triggered is True
    assert "timed out" in planner_run.fallback_reason
    assert [panel.caption for panel in story.panels] == ["Setup", "Complication", "Response", "Resolution"]


def test_plan_story_falls_back_when_lm_is_unavailable(monkeypatch, tmp_path):
    _set_lm_env(monkeypatch)

    def raise_unavailable(self, request):
        raise ConnectionError("offline")

    monkeypatch.setattr(story_planner.LMStoryPlanner, "_request_payload", raise_unavailable)
    request = ComicRequest(
        theme="A fox learns to cook",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    _, planner_run = story_planner.plan_story(request)

    assert planner_run.actual_mode == "rule_based"
    assert "unavailable" in planner_run.fallback_reason


def test_validate_lm_storyboard_payload_rejects_explicit_character_conflict(tmp_path):
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        character="戴红围巾的小兔子",
        output_dir=tmp_path,
    )

    try:
        story_planner.validate_lm_storyboard_payload(_valid_lm_payload(subject="小兔子"), request)
    except story_planner.LMPlanningError as exc:
        assert "conflicts with explicit character" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected explicit-character conflict rejection")


def test_validate_lm_storyboard_payload_rejects_page_level_layout_terms(tmp_path):
    request = ComicRequest(
        theme="记录同一只流浪橘猫在四季中的变化，特征保持一致",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )
    payload = json.loads(_valid_lm_payload(subject="流浪橘猫"))
    payload["panels"][0]["scene_description"] = "a four-panel comic page showing every season at once"

    try:
        story_planner.validate_lm_storyboard_payload(json.dumps(payload, ensure_ascii=False), request)
    except story_planner.LMPlanningError as exc:
        assert "page-level or multi-panel instructions" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected page-level layout rejection")


def test_validate_lm_storyboard_payload_rejects_placeholder_subject(tmp_path):
    request = ComicRequest(
        theme="主角获得超能力，却只用来多睡五分钟。",
        planner_mode="lm_assisted",
        output_dir=tmp_path,
    )

    try:
        story_planner.validate_lm_storyboard_payload(_valid_lm_payload(subject="Protagonist"), request)
    except story_planner.LMPlanningError as exc:
        assert "subject is too generic" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected placeholder subject rejection")


def test_validate_lm_storyboard_payload_rejects_english_panels_for_zh_request(tmp_path):
    request = ComicRequest(
        theme="主角获得超能力，却只用来多睡五分钟。",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )
    payload = json.dumps(
        {
            "subject": "主角",
            "panels": [
                {
                    "caption": "Monday morning",
                    "dialogue": "Already? Just five more minutes.",
                    "scene_description": "A messy bedroom with a loud alarm clock.",
                    "action": "Reach for the clock.",
                    "emotion": "Tired",
                    "camera_framing": "close-up",
                    "visual_description": "Messy hair and dim morning light.",
                },
                {
                    "caption": "Memory",
                    "dialogue": "I can stop time.",
                    "scene_description": "The protagonist raises a glowing hand.",
                    "action": "Prepare to use the power.",
                    "emotion": "Smug",
                    "camera_framing": "medium shot",
                    "visual_description": "Blue light around the hand.",
                },
                {
                    "caption": "Frozen room",
                    "dialogue": "Zzz...",
                    "scene_description": "The room freezes while the protagonist sleeps.",
                    "action": "Hide under the blanket.",
                    "emotion": "Peaceful",
                    "camera_framing": "wide shot",
                    "visual_description": "Dust hangs still in the air.",
                },
                {
                    "caption": "Too late",
                    "dialogue": "Oh no!",
                    "scene_description": "The clock jumps ahead and the protagonist panics.",
                    "action": "Leap out of bed.",
                    "emotion": "Panicked",
                    "camera_framing": "low angle",
                    "visual_description": "The bed is in chaos.",
                },
            ],
        },
        ensure_ascii=False,
    )

    try:
        story_planner.validate_lm_storyboard_payload(payload, request)
    except story_planner.LMPlanningError as exc:
        assert "must be written in Chinese" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected Chinese-language rejection")


def test_validate_lm_storyboard_payload_rejects_invented_power_origin(tmp_path):
    request = ComicRequest(
        theme="主角获得超能力，却只用来多睡五分钟。",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )
    payload = json.dumps(
        {
            "subject": "小明",
            "panels": [
                {
                    "caption": "小明在路边捡到一块奇怪的手表。",
                    "dialogue": "这是什么？",
                    "scene_description": "小明在放学路上蹲下捡起一个发光手表。",
                    "action": "他端详手表。",
                    "emotion": "好奇",
                    "camera_framing": "中景",
                    "visual_description": "路边和发光手表。",
                },
                {
                    "caption": "他发现按下按钮可以暂停时间。",
                    "dialogue": "我能暂停时间！",
                    "scene_description": "小明按下手表按钮，周围静止。",
                    "action": "他尝试新能力。",
                    "emotion": "惊喜",
                    "camera_framing": "近景",
                    "visual_description": "手表发光，空气凝固。",
                },
                {
                    "caption": "清晨他用能力赖床。",
                    "dialogue": "再睡五分钟。",
                    "scene_description": "小明在床上按下手表继续睡。",
                    "action": "他钻回被窝。",
                    "emotion": "满足",
                    "camera_framing": "中景",
                    "visual_description": "闹钟停在七点。",
                },
                {
                    "caption": "结果还是迟到了。",
                    "dialogue": "糟了！",
                    "scene_description": "小明匆忙冲出门。",
                    "action": "他狼狈出门。",
                    "emotion": "慌张",
                    "camera_framing": "中景",
                    "visual_description": "书包晃动，表情慌乱。",
                },
            ],
        },
        ensure_ascii=False,
    )

    try:
        story_planner.validate_lm_storyboard_payload(payload, request)
    except story_planner.LMPlanningError as exc:
        assert "invented an unsupported origin or prop" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected invented-origin rejection")


def test_validate_lm_storyboard_payload_rejects_sleep_theme_without_sleep_anchor(tmp_path):
    request = ComicRequest(
        theme="主角获得超能力，却只用来多睡五分钟。",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )
    payload = json.dumps(
        {
            "subject": "小明",
            "panels": [
                {
                    "caption": "小明在操场展示能力。",
                    "dialogue": "看我的。",
                    "scene_description": "小明在操场上举起双手。",
                    "action": "他展示超能力。",
                    "emotion": "得意",
                    "camera_framing": "中景",
                    "visual_description": "同学围观。",
                },
                {
                    "caption": "同学们十分惊讶。",
                    "dialogue": "太厉害了！",
                    "scene_description": "所有人都看着小明。",
                    "action": "大家鼓掌。",
                    "emotion": "兴奋",
                    "camera_framing": "中景",
                    "visual_description": "操场气氛热烈。",
                },
                {
                    "caption": "他继续练习。",
                    "dialogue": "我还能更强。",
                    "scene_description": "小明在空地上继续测试能力。",
                    "action": "他释放能量。",
                    "emotion": "专注",
                    "camera_framing": "远景",
                    "visual_description": "光效夸张。",
                },
                {
                    "caption": "大家为他欢呼。",
                    "dialogue": "冠军！",
                    "scene_description": "小明站在人群中央。",
                    "action": "他挥手致意。",
                    "emotion": "开心",
                    "camera_framing": "中景",
                    "visual_description": "操场上人群庆祝。",
                },
            ],
        },
        ensure_ascii=False,
    )

    try:
        story_planner.validate_lm_storyboard_payload(payload, request)
    except story_planner.LMPlanningError as exc:
        assert "sleep-and-wakeup core" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected sleep-anchor rejection")


def test_validate_lm_storyboard_payload_rejects_day_in_life_theme_without_school_anchor(tmp_path):
    request = ComicRequest(
        theme="一只小兔子上学的一天",
        planner_mode="lm_assisted",
        lang="zh",
        output_dir=tmp_path,
    )
    payload = json.dumps(
        {
            "subject": "小兔子",
            "panels": [
                {
                    "caption": "清晨散步",
                    "dialogue": "今天空气真好。",
                    "scene_description": "小兔子在河边慢慢散步。",
                    "action": "它看着水面发呆。",
                    "emotion": "平静",
                    "camera_framing": "中景",
                    "visual_description": "河边树影安静。",
                },
                {
                    "caption": "路边休息",
                    "dialogue": "再坐一会儿。",
                    "scene_description": "小兔子坐在长椅上晒太阳。",
                    "action": "它喝着果汁。",
                    "emotion": "放松",
                    "camera_framing": "中景",
                    "visual_description": "公园长椅和草地。",
                },
                {
                    "caption": "午后看云",
                    "dialogue": "那朵云像棉花。",
                    "scene_description": "小兔子躺在山坡上看天空。",
                    "action": "它伸手指向云朵。",
                    "emotion": "惬意",
                    "camera_framing": "远景",
                    "visual_description": "山坡和白云。",
                },
                {
                    "caption": "傍晚回家",
                    "dialogue": "今天很轻松。",
                    "scene_description": "小兔子沿着小路慢慢回家。",
                    "action": "它踢着路边的小石子。",
                    "emotion": "满足",
                    "camera_framing": "中景",
                    "visual_description": "夕阳下的小路。",
                },
            ],
        },
        ensure_ascii=False,
    )

    try:
        story_planner.validate_lm_storyboard_payload(payload, request)
    except story_planner.LMPlanningError as exc:
        assert "core scene progression" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected day-in-the-life anchor rejection")
