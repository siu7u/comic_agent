# Quickstart: Real image provider integration

## Prerequisites

- Python 3.11+
- Project dependencies installed
- A shell environment that can export provider credentials

## Install

```bash
python3 -m pip install -e .[dev]
```

## Mock Verification Run

Use the existing mock-safe flow first:

```bash
comic-agent generate \
  --theme "A fox learns to cook" \
  --out ./tmp/mock-run
```

Expected result:

- four panel PNG files
- `comic.png`
- `metadata.json`
- metadata identifies the mock provider path

## Real Provider Preparation

Before a real-provider run:

1. Export the required environment variables for the selected provider.
2. Confirm the provider selection input is set to the real provider.
3. Keep the same story and prompt inputs used by the existing CLI flow.
4. Expect the pipeline to rewrite panel-generation prompts into single-scene
   full-frame image instructions before each provider call.

## Real Provider Smoke Run

```bash
comic-agent generate \
  --theme "A frog builds a kite" \
  --provider wanx \
  --style "watercolor" \
  --character "small green frog with a yellow scarf" \
  --image-prompt "misty dawn, soft light, gentle storybook mood" \
  --out ./tmp/real-run
```

Expected result:

- four non-placeholder panel PNG files
- `comic.png`
- `metadata.json`
- metadata identifies the real provider and provider mode
- each panel prompt in metadata is a single-scene prompt without page-level
  comic layout instructions

## Single-Scene Prompt Check

For themes that imply progression across four panels, verify that each provider
call still targets one scene only.

Example theme:

```text
记录同一只流浪橘猫在四季中的变化，特征保持一致
```

Expected prompt behavior:

- panel 1 focuses on spring
- panel 2 focuses on summer
- panel 3 focuses on autumn
- panel 4 focuses on winter
- each `final_image_prompt` includes anti-collage constraints
- no `final_image_prompt` includes page-level layout wording such as
  four-panel layout, grid, split-screen, or montage

## Failure Verification

Unset the required provider credentials and run the same command with the real
provider selected.

Expected result:

- the command fails before panel generation begins
- the error message explains the missing environment setup

## Documentation Check

Confirm repository-root `README.md` documents:

- mock vs real provider usage
- required environment setup for the real provider
- provider selection behavior
- the testing boundary that keeps automated tests on the mock provider

## Suggested Verification Commands

```bash
pytest tests/unit
pytest tests/integration/test_mock_pipeline.py
python3 -m compileall src tests
```
