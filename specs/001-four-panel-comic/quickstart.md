# Quickstart: Four-panel comic generation MVP

## Prerequisites

- Python 3.11+
- Project dependencies installed

## Install

```bash
python3 -m pip install -e .[dev]
```

## Example Command

```bash
comic-agent generate \
  --theme "A shy cat learns to skateboard" \
  --style "watercolor" \
  --character "small white cat with red scarf" \
  --image-prompt "warm afternoon light, playful city park" \
  --panel-prompt-2 "close-up of the cat wobbling but determined" \
  --reference-image ./tmp/reference.png \
  --lang zh \
  --out ./tmp/comic-output
```

## Expected Outputs

After a successful run, `./tmp/comic-output/` contains:

- `panel-1.png`
- `panel-2.png`
- `panel-3.png`
- `panel-4.png`
- `comic.png`
- `metadata.json`

## Documentation Check

- Confirm repository-root `README.md` reflects the current install command, CLI
  arguments, example command shape, expected output files, MockImageProvider MVP
  boundary, reference-image handling, and test commands

## Verification Checks

1. Confirm four panel PNG files exist and each is `512x512`.
2. Confirm `comic.png` exists and is `1054x1054`.
3. Confirm `metadata.json` contains:
   - request inputs
   - `character_bible`
   - `style_bible`
   - four panel records
   - per-panel `prompt_source`
   - provider name
   - retry counts
   - image paths

## Suggested Test Commands

```bash
pytest tests/unit/test_prompt_builder.py
pytest tests/unit/test_layout_composer.py
pytest tests/integration/test_mock_pipeline.py
python3 -m compileall src tests
```

## Safety Check Example

- Run the command with intentionally unsafe theme text and confirm the command
  rejects the request before story generation.
