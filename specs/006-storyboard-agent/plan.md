# Implementation Plan: StoryboardAgent for four-panel story expansion

**Branch**: `006-storyboard-agent` | **Date**: 2026-05-29 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/006-storyboard-agent/spec.md)
**Input**: Feature specification from `/specs/006-storyboard-agent/spec.md`

## Summary

Introduce a lightweight internal `StoryboardAgent` that expands short user
themes into exactly four concrete panel story beats before prompt generation.
The design keeps the existing CLI, providers, layout, and metadata pipeline
contracts intact while replacing repeated template scenes with distinct
storyboard-ready panel moments for day-in-the-life, seasonal, journey,
problem-solving, and fallback themes, and allows the LM-assisted path to
feed one structured semantic result into the same expansion flow.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Standard library, Pillow, pytest, existing prompt and provider pipeline code  
**Storage**: Local filesystem outputs and metadata only  
**Testing**: pytest  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Keep storyboard expansion effectively instantaneous
relative to image generation and preserve the existing single-run CLI workflow  
**Constraints**: No external agent framework, exactly four panels per run,
concrete single-scene panel descriptions only, no page-level layout language
inside panel descriptions, preserve existing provider interfaces and final
`1054x1054` comic layout with `10px` `田`-shaped grid border, and keep a
rule-based fallback when LM-assisted semantic parsing is unavailable or invalid  
**Scale/Scope**: One request per run, one detected storyboard structure per
request, four panel beats per story, deterministic keyword- and rule-based
story expansion only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. The feature has a completed `spec.md`, this
  `plan.md`, and will receive `tasks.md` before implementation.
- `CLI MVP and Simplicity`: Pass. The feature remains fully inside the existing
  CLI pipeline and adds one internal planning component rather than a larger
  orchestration layer.
- `Modular Comic Pipeline`: Pass. The design strengthens the boundary between
  storyboard planning and downstream prompt/provider stages without changing
  layout or export responsibilities.
- `Verifiable Core Logic`: Pass. Rule-based semantics, LM-assisted semantic
  validation, and four-panel expansion can all be covered with `pytest` plus
  mock-safe integration tests.
- `Minimal Provider Abstraction`: Pass. Providers are unaffected by this
  feature and remain external to story expansion.
- `Character and Style Consistency`: Pass. The StoryboardAgent improves panel
  scene quality while preserving downstream character bible and style bible use.
- `Safety Before Generation`: Pass. Unsafe themes remain rejected before
  downstream generation, and storyboard scenes must avoid layout or collage
  instructions that would weaken single-scene prompting.
- `Real Command Verification`: Pass. Implementation will end with targeted
  storyboard tests, compatibility checks, and `python3 -m compileall src tests`.
- `No Speculative Features`: Pass. No new provider, no external agent
  framework, no CLI expansion, and no background workflow are introduced.
- `Documentation Stays Aligned`: Pass. README updates are required only if the
  documented architecture or contributor workflow changes.

## Project Structure

### Documentation (this feature)

```text
specs/006-storyboard-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── storyboard-expansion-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md
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
    │   ├── exporter.py
    │   └── panel_validation.py
    └── providers/
        ├── base.py
        ├── mock.py
        └── real_provider.py

tests/
├── integration/
│   └── test_mock_pipeline.py
└── unit/
    ├── test_story_planner.py
    ├── test_prompt_builder.py
    ├── test_provider_selection.py
    ├── test_real_provider.py
    └── ...
```

**Structure Decision**: Keep the existing single-package CLI layout. The main
feature work stays centered in `src/comic_agent/pipeline/story_planner.py` with
supporting compatibility checks in existing unit and integration tests.

## Consistency and Safety Design

**Character Bible**: The StoryboardAgent produces a stronger subject anchor and
concrete scene progression so downstream character bible generation can define
consistent visual traits against a stable main subject.  
**Style Bible**: Style bible generation remains downstream, but storyboard
output must avoid page-level layout language so style and prompt generation stay
focused on one scene per image.  
**Safety Strategy**: Unsafe themes remain rejected before provider generation.
Storyboard expansion must not add collage, grid, comic-page, or multi-scene
instructions that widen unsafe or off-spec content.  
**Metadata Traceability**: Existing metadata export remains compatible. Planned
story fields become more specific and inspectable, but no new required metadata
artifact is introduced by this feature alone.  
**Compatibility Boundary**: `build_story_structure(request)` remains the
compatibility entrypoint, with the new StoryboardAgent behind it.  
**Documentation Traceability**: `README.md` changes only if contributor-facing
architecture or workflow wording needs to mention the StoryboardAgent.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/006-storyboard-agent/research.md) for resolved decisions on subject extraction, semantic unification, structure detection priority, concrete panel-beat expansion, compatibility delegation, and mock-safe verification.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/006-storyboard-agent/data-model.md)
- Storyboard expansion contract: [contracts/storyboard-expansion-contract.md](/home/caizh/programming/python_code/comic_agent/specs/006-storyboard-agent/contracts/storyboard-expansion-contract.md)
- Verification guide: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/006-storyboard-agent/quickstart.md)
- Contributor-facing contract: `README.md` at repository root if architecture wording changes

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. The design adds one internal
  storyboard component and no new runtime surface.
- `Modular Comic Pipeline`: Still passes. Storyboard expansion stays isolated
  behind one planning entrypoint and preserves prompt/provider boundaries.
- `Verifiable Core Logic`: Still passes. Rule-based semantics, LM-assisted
  semantic validation, and panel expansion remain testable.
- `Minimal Provider Abstraction`: Still passes. Providers are unchanged and
  continue to consume prompt output only.
- `Character and Style Consistency`: Still passes. Better subject resolution
  and stronger panel beats improve downstream consistency without moving bible
  ownership out of prompt generation.
- `Safety Before Generation`: Still passes. Storyboard output explicitly avoids
  multi-scene and page-layout instructions and keeps upstream safety intact.
- `Documentation Stays Aligned`: Still passes. README updates remain a tracked
  deliverable only if architecture wording changes.
- `No Speculative Features`: Still passes. The structure set is intentionally
  narrow and rule-based, with no live planning model.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
