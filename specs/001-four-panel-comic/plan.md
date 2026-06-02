# Implementation Plan: Four-panel comic generation MVP

**Branch**: `001-four-panel-comic` | **Date**: 2026-05-28 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/001-four-panel-comic/spec.md)
**Input**: Feature specification from `/specs/001-four-panel-comic/spec.md`

## Summary

Build a CLI-only MVP that accepts a comic theme plus optional style, character,
prompt-guidance, and one global reference image, then produces a four-panel
story package with per-panel prompts, four panel PNGs, one composed 2x2 comic
PNG, `metadata.json`, and a user-facing `README.md`. The implementation keeps a
modular pipeline with separate story planning, prompt generation, safety
handling, mock image generation, layout composition, export, and documentation
deliverables.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pillow, pytest  
**Storage**: Local filesystem outputs only  
**Testing**: pytest  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Complete a mock-provider run for one four-panel request in under 10 seconds on a typical local development machine  
**Constraints**: Fixed 512x512 panel PNGs, fixed 1054x1054 final PNG, one request per CLI invocation, no database, no queue, no web UI, no live provider integration in MVP, README must stay aligned with user-facing behavior  
**Scale/Scope**: Single user, single local run, exactly four panels, one global reference image, outputs contained in one selected directory

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. `spec.md` is clarified and this `plan.md` defines
  the implementation scope before coding; `tasks.md` must be regenerated next to
  reflect the README deliverable.
- `CLI MVP and Simplicity`: Pass. Scope remains one CLI command, local file
  outputs, one mock provider, and one README deliverable. No web, queue,
  database, or framework work is included.
- `Modular Comic Pipeline`: Pass. Design separates story planning, prompt
  building, safety, image provider, layout composition, export, and
  documentation responsibilities.
- `Verifiable Core Logic`: Pass. `pytest` covers prompt building, reference-image
  validation, layout composition, metadata export, and mock pipeline behavior.
- `Minimal Provider Abstraction`: Pass. A single image-provider interface is
  retained with `MockImageProvider` as the only concrete MVP implementation.
- `Character and Style Consistency`: Pass. `character_bible` and `style_bible`
  are generated once per request and injected into every panel prompt.
- `Safety Before Generation`: Pass. Unsafe theme input is rejected before story
  generation; unsafe prompt guidance is rejected or minimally rewritten before
  provider execution.
- `Real Command Verification`: Pass. Implementation must finish with at least a
  targeted `pytest` command or a CLI demo command.
- `No Speculative Features`: Pass. Real providers, per-panel reference images,
  API-key handling, provider selection, and background execution are deferred.
- `Documentation Stays Aligned`: Pass. `README.md` is now a planned deliverable
  and must be updated alongside user-facing CLI, setup, output, provider, and
  test-command changes.

## Project Structure

### Documentation (this feature)

```text
specs/001-four-panel-comic/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── tasks.md

README.md               # User-facing project contract for setup and usage
```

### Source Code (repository root)

```text
README.md
pyproject.toml
src/
└── comic_agent/
    ├── cli/
    │   └── generate.py
    ├── models/
    │   ├── bibles.py
    │   ├── comic_request.py
    │   ├── metadata.py
    │   └── panel.py
    ├── pipeline/
    │   ├── story_planner.py
    │   ├── prompt_builder.py
    │   ├── safety.py
    │   ├── composer.py
    │   └── exporter.py
    └── providers/
        ├── base.py
        └── mock.py

tests/
├── integration/
│   └── test_mock_pipeline.py
└── unit/
    ├── test_prompt_builder.py
    ├── test_reference_image_validation.py
    ├── test_layout_composer.py
    └── test_metadata_export.py
```

**Structure Decision**: Use one Python package under `src/comic_agent/` so the
pipeline stages remain separate without adding multi-package overhead. Keep
`README.md` at repository root as the user-facing contract, distinct from
feature-internal planning documents under `specs/`.

## Consistency and Safety Design

**Character Bible**: A normalized request-level structure containing canonical
character name/description, recurring appearance traits, and consistency notes
derived from `--character`, `--theme`, and any compatible prompt guidance.  
**Style Bible**: A normalized request-level structure containing artistic style,
tone, atmosphere, composition cues, and recurring visual constraints derived
from `--style` and compatible prompt guidance.  
**Safety Strategy**: Validate required input first, reject unsafe theme input
before story planning, then inspect global/per-panel prompt guidance for unsafe
or contradictory content and either reject or minimally rewrite before prompt
finalization and provider execution.  
**Metadata Traceability**: Export request inputs, normalized bibles, story plan,
panel content, prompt sources, rewrite warnings, reference-image path, provider
name, retry counts, panel image paths, and final comic path in `metadata.json`.  
**Documentation Traceability**: Keep `README.md` synchronized with CLI usage,
setup steps, output files, provider behavior, reference-image handling, module
responsibilities, and test commands whenever those user-facing details change.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/001-four-panel-comic/research.md) for resolved decisions covering CLI parsing, prompt-source handling, fixed-canvas composition, deterministic mock image generation, metadata shape, and README alignment.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/001-four-panel-comic/data-model.md)
- CLI contract: [contracts/cli-contract.md](/home/caizh/programming/python_code/comic_agent/specs/001-four-panel-comic/contracts/cli-contract.md)
- Validation flow and demo steps: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/001-four-panel-comic/quickstart.md)
- Contributor and user-facing contract: `README.md` at repository root

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. Design keeps a single CLI entrypoint,
  files-only outputs, and one README deliverable.
- `Modular Comic Pipeline`: Still passes. Data model and contracts map cleanly to
  distinct pipeline stages and separate documentation responsibility.
- `Verifiable Core Logic`: Still passes. Every critical stage has a direct test
  target and the mock provider remains deterministic.
- `Minimal Provider Abstraction`: Still passes. Only one provider interface and
  one mock implementation are defined.
- `Character and Style Consistency`: Still passes. Shared bibles are explicit
  request-level entities and prompt inputs.
- `Safety Before Generation`: Still passes. Safety gating occurs before provider
  execution and reference-image handling remains limited to file validation.
- `Documentation Stays Aligned`: Still passes. The plan explicitly requires
  README creation and README synchronization for user-facing changes.
- `No Speculative Features`: Still passes. Deferred items are documented but not
  added to the runtime implementation scope.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
