# CLI Contract: Real image provider integration

## Command

`comic-agent generate`

## Existing Required Arguments

- `--theme <text>`

## Existing Optional Arguments

- `--style <text>`
- `--character <text>`
- `--image-prompt <text>`
- `--panel-prompt-1 <text>`
- `--panel-prompt-2 <text>`
- `--panel-prompt-3 <text>`
- `--panel-prompt-4 <text>`
- `--reference-image <path>`
- `--lang <code>`
- `--out <path>`

## New Provider Selection Contract

- The CLI must expose a user-facing way to select the image provider for a run
- The contract must support:
  - explicit selection of the mock provider
  - explicit selection of the real provider
  - a predictable default of the real provider for normal CLI runs
  - explicit mock selection for automated tests and credential-free runs

## Real Provider Setup Contract

- Real provider credentials must be read from environment variables
- Missing or invalid environment configuration must produce a clear setup error
  before any panel generation request is sent
- Secret values must not be echoed into normal command output or metadata

## Successful Behavior

- All existing comic generation outputs remain unchanged in shape:
  - four panel PNG files
  - one final comic PNG
  - one `metadata.json`
- Successful runs must record:
  - provider name
  - whether provider behavior was mock or real
  - per-panel retry counts
- Real-provider runs must still use the same four generated panel prompts and
  final 2x2 composition flow
- Each provider call must receive one single-scene full-frame panel prompt, not
  a page layout request
- Final panel prompts must include explicit anti-collage constraints covering:
  - no collage
  - no split-screen
  - no grid
  - no internal comic layout
  - no four-panel layout inside the image
  - no montage
  - no seasonal comparison layout
  - no text labels, captions, or speech bubbles

## Error Behavior

- Selecting the real provider without valid environment configuration returns a
  clear configuration error
- Real-provider image failures respect the existing retry limit
- Unusable provider image output fails the run safely and clearly
- Unsafe theme or prompt input is still blocked or rewritten before any
  provider request
- Page-level layout instructions must be excluded from provider-facing panel
  prompts even though the final composed output remains a 2x2 comic grid

## Metadata Contract

`metadata.json` must continue to include existing request, story, prompt, and
artifact fields, and must additionally support:

- run-level provider mode
- run-level provider name
- per-panel retry outcomes
- provider failure information when available
- the exact final provider-facing panel prompt used for each generated panel

## Documentation Contract

`README.md` must describe:

- how to prepare environment variables for the real provider
- how to select mock vs real provider
- that automated tests remain mock-first
- that reference-image input remains outside real image-to-image scope
