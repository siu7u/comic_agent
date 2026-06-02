# Quickstart: LM-assisted story planner

## Goal

Verify that users can explicitly opt into LM-assisted planning while the
existing rule-based planner remains the default and automatic fallback path.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- A local environment that can set required LM configuration variables for
  manual runs

## Install

```bash
python3 -m pip install -e .[dev]
```

## Default Rule-Based Verification

Confirm the current default path remains unchanged:

```bash
comic-agent generate \
  --theme "A fox learns to cook" \
  --provider mock \
  --out ./tmp/rule-based-run
```

Expected result:

- the run completes without enabling LM-assisted planning
- the existing rule-based planner produces the story structure
- metadata reflects the requested and actual planner mode as rule-based

## LM-Assisted Verification

Set the required LM environment variables, then run a manual opt-in planning
request using the planner-selection flag.

Expected result:

- the system attempts LM-assisted planning first
- the LM returns one strict JSON planning result
- the result is validated before prompt generation
- metadata records both the requested planner mode and the actual planner used

## Fallback Verification

Simulate one or more invalid LM conditions:

- malformed JSON
- fewer than four panels
- missing panel fields
- page-level layout instructions
- timeout or unavailable LM response

Expected result:

- the system automatically falls back to the rule-based planner
- the run still produces a valid four-panel story structure
- metadata records the requested LM-assisted mode, actual rule-based mode, and
  fallback reason

## Suggested Verification Commands

```bash
pytest tests/unit/test_story_planner.py
pytest tests/unit/test_prompt_builder.py
pytest tests/unit/test_metadata_export.py
pytest tests/integration/test_mock_pipeline.py
python3 -m compileall src tests
```

## README Check

Confirm repository-root `README.md` documents:

- the planner-selection CLI flag
- environment-based LM configuration for manual runs
- default rule-based behavior
- fallback behavior
- mock-safe automated testing expectations
