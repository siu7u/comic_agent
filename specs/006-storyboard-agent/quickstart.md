# Quickstart: StoryboardAgent for four-panel story expansion

## Goal

Verify that simple themes are expanded into four concrete storyboard panels
through a lightweight internal StoryboardAgent while preserving compatibility
with the current comic pipeline.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- Local test environment without any required provider credentials

## Install

```bash
python3 -m pip install -e .[dev]
```

## Storyboard Verification Themes

Use these representative themes during implementation verification:

- `一只小兔子上学的一天`
- `记录同一只流浪橘猫在四季中的变化，特征保持一致`
- `一只狐狸放飞灯笼`
- `机器人修好城市的灯`
- one generic fallback theme such as `A fox learns to cook`

## Expected Storyboard Outcomes

### Day-in-the-Life Theme

For `一只小兔子上学的一天`, expect:

- exactly four panels
- captions `Morning`, `On the Way`, `At School`, `Going Home`
- scenes covering departure from home, journey to school, classroom or school
  activity, and return home
- no repeated generic scene text across all panels

### Seasonal Theme

For `记录同一只流浪橘猫在四季中的变化，特征保持一致`, expect:

- exactly four panels
- captions `Spring`, `Summer`, `Autumn`, `Winter`
- each panel describes one season only
- no panel asks for all seasons in one image

### Journey Theme

For `一只狐狸放飞灯笼`, expect:

- exactly four panels
- captions that follow a departure-to-resolution progression
- scenes covering preparation, release or encounter, turning point, and final
  resolution
- each scene reads as a concrete visual moment

### Problem-Solving Theme

For `机器人修好城市的灯`, expect:

- exactly four panels
- captions `Problem`, `Search`, `Solution`, `Payoff`
- scenes covering visible failure, investigation, repair action, and resolved
  city lighting
- no panel falls back to vague phrases like `encounters the setup of ...`

### Fallback Theme

For a generic fallback prompt, expect:

- exactly four panels
- captions `Setup`, `Complication`, `Response`, `Resolution`
- distinct concrete scenes rather than four copies of the same template

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
workflow wording needs to mention the new StoryboardAgent component.
