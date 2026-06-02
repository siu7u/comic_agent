# CLI Contract: Four-panel comic generation MVP

## Command

`comic-agent generate`

## Required Arguments

- `--theme <text>`
  - Required comic theme or story idea

## Optional Arguments

- `--style <text>`
- `--character <text>`
- `--image-prompt <text>`
- `--panel-prompt-1 <text>`
- `--panel-prompt-2 <text>`
- `--panel-prompt-3 <text>`
- `--panel-prompt-4 <text>`
- `--reference-image <path>`
- `--lang <code>`
  - Defaults to `zh`
- `--out <path>`
  - Defaults to a generated output directory if not provided by implementation choice

## Successful Behavior

- Validates request inputs
- Generates exactly four panel records
- Produces four `512x512` panel PNG files
- Produces one `1054x1054` final comic PNG
- Writes `metadata.json`
- Stores all artifacts under the resolved output directory

## Error Behavior

- Missing `--theme` returns a clear validation error
- Unreadable or unsupported `--reference-image` returns a clear validation error
- Unsafe theme input is rejected before story generation
- Unsafe prompt guidance is rejected or minimally rewritten before provider execution
- Panel image generation retries at most two times before the command fails

## Metadata Contract

`metadata.json` must include:

- normalized request fields
- request-level `character_bible`
- request-level `style_bible`
- story structure with exactly four panels
- per-panel `prompt_source`
- per-panel final prompt text
- per-panel warnings and retry count
- `reference_image_path` when provided
- provider name
- panel image paths
- final comic image path

## Explicit MVP Deferrals

- per-panel reference image arguments
- live provider credentials
- provider selection flags
- web or background execution modes

## Documentation Contract

- `README.md` at repository root must describe this CLI contract, setup steps,
  output files, provider boundary, reference-image handling, and test commands
- README updates are required when this CLI contract changes in a user-visible way
