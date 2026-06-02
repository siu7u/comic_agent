# Research: Four-panel comic generation MVP

## Decision 1: Use one top-level CLI command with flat flags

- **Decision**: Expose a single command for generation with flat flags for theme,
  optional prompt inputs, optional reference image, language, and output path.
- **Rationale**: The MVP handles one request type only, so subcommands add
  ceremony without reducing ambiguity.
- **Alternatives considered**:
  - Separate `generate` and `compose` commands: rejected because the spec defines
    one end-to-end request flow.
  - JSON file input only: rejected because it raises the entry cost for MVP use.

## Decision 2: Keep provider behavior mock-only and deterministic

- **Decision**: Implement only `MockImageProvider` and make its placeholder image
  output deterministic for the same panel input.
- **Rationale**: Determinism makes tests stable and allows the pipeline to run
  without external credentials or network dependencies.
- **Alternatives considered**:
  - Add live provider support now: rejected because it violates the clarified MVP
    boundary.
  - Randomized placeholder images: rejected because they weaken test assertions.

## Decision 3: Represent prompt provenance explicitly in metadata

- **Decision**: Record per-panel `prompt_source`, rewritten prompt text,
  warnings, provider identity, retry count, and reference-image path in
  `metadata.json`.
- **Rationale**: The spec requires transparency for merged prompts, safety
  rewrites, and mock/image-guided runs.
- **Alternatives considered**:
  - Store only final prompts: rejected because it hides safety and merge
    behavior.
  - Store provenance only at request level: rejected because prompt handling is
    panel-specific.

## Decision 4: Compose the final comic on a fixed border-inclusive canvas

- **Decision**: Use four 512x512 panel PNGs and compose them into a 1054x1054
  final PNG with a 10-pixel outer border plus 10-pixel vertical and horizontal
  dividers.
- **Rationale**: The clarified spec defines exact geometry, which simplifies
  layout code and gives tests direct pixel-size expectations.
- **Alternatives considered**:
  - Borderless 1024x1024 grid: rejected because it conflicts with clarified
    layout requirements.
  - Flexible canvas sizing: rejected because it would complicate output
    contracts and tests.

## Decision 5: Generate shared bibles once per request

- **Decision**: Build `character_bible` and `style_bible` once from request
  inputs, then inject them into each panel prompt.
- **Rationale**: Request-level normalization is the simplest way to keep all four
  panels consistent and to support prompt rewriting rules.
- **Alternatives considered**:
  - Derive bibles independently per panel: rejected because it risks drift.
  - Skip explicit bibles and rely on prompt text alone: rejected because the spec
    requires shared consistency structures.

## Decision 6: Limit reference-image handling to validation and metadata

- **Decision**: Accept one global reference image, validate that the path exists
  and points to a supported image file, and record it in metadata without using
  it to transform mock outputs.
- **Rationale**: This preserves the future image-to-image integration boundary
  while keeping the MVP simple.
- **Alternatives considered**:
  - Per-panel reference images: rejected because clarification deferred them.
  - Real mock image-to-image behavior: rejected because it adds fake complexity
    without user value in this MVP.
