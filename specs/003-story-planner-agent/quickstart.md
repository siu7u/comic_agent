# Quickstart: StoryPlannerAgent refactor

## Goal

Verify that story planning now produces four concrete panel scenes through a
lightweight internal planner while preserving compatibility with the existing
pipeline.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- Local test environment without any required provider credentials

## Install

```bash
python3 -m pip install -e .[dev]
```

## Planner Verification Themes

Use these representative themes during implementation verification:

- `一只小兔子上学的一天`
- `记录同一只流浪橘猫在四季中的变化，特征保持一致`
- `狐狸参加篮球赛，投进绝杀三分`
- one generic fallback theme such as `A fox learns to cook`
- one journey or growth theme such as `A young bird's growth journey`

## Expected Planning Outcomes

### School-day Theme

For `一只小兔子上学的一天`, expect:

- exactly four panels
- captions `Morning`, `On the Way`, `At School`, `Going Home`
- scenes covering departure, journey, school activity, and return or end of day
- no repeated generic `scene_description` across all panels

### Seasonal Theme

For `记录同一只流浪橘猫在四季中的变化，特征保持一致`, expect:

- exactly four panels
- captions `Spring`, `Summer`, `Autumn`, `Winter`
- each panel describes one season only
- no panel asks for all seasons in one image

### Fallback Theme

For a generic fallback theme, expect:

- exactly four panels
- captions `Setup`, `Complication`, `Response`, `Resolution`
- distinct concrete scenes rather than four copies of the same template

### Competition Theme

For `狐狸参加篮球赛，投进绝杀三分`, expect:

- exactly four panels
- captions `Opening`, `Pressure`, `Climax`, `Finish`
- scenes covering pre-match setup, in-game pressure, the decisive shot, and
  the immediate visible outcome
- no panel falls back to vague phrases like `encounters the setup of ...`

## Compatibility Check

Confirm that the existing compatibility entrypoint still works:

- `build_story_structure(request)` returns a valid `StoryStructure`
- downstream prompt-building tests still consume the planned panels
- no provider credential or network dependency is introduced

## Suggested Verification Commands

```bash
pytest tests/unit/test_story_planner.py
pytest tests/unit/test_prompt_builder.py
pytest tests/integration/test_mock_pipeline.py
python3 -m compileall src tests
```

## README Check

Update repository-root `README.md` only if contributor-facing architecture or
workflow wording needs to mention the new internal planner component.
