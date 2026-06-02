# Implementation Plan: StoryPlannerAgent refactor

**Branch**: `002-real-image-provider` | **Date**: 2026-05-29 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/003-story-planner-agent/spec.md)
**Input**: Feature specification from `/specs/003-story-planner-agent/spec.md`

## Summary

Refactor the current template-heavy story planner into a lightweight internal
`StoryPlannerAgent` that deterministically normalizes requests, extracts the
main subject, detects a small set of story intent types, and emits exactly four
concrete visual panel beats while preserving the existing prompt, provider,
layout, and metadata pipeline contracts.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Standard library, Pillow, pytest  
**Storage**: Local filesystem outputs and metadata only  
**Testing**: pytest  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Preserve the current single-run CLI workflow and keep
story planning effectively instantaneous compared with image generation  
**Constraints**: No external agent framework, no live model calls, exactly four
panels per run, no page-level layout instructions in planned scenes, preserve
the current `1054x1054` final comic image with `10px` `田`-shaped grid border  
**Scale/Scope**: One request per run, one inferred story intent per request,
exactly four planned panels, deterministic rule-based planning only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. The feature has a completed `spec.md`, this
  `plan.md`, and tasks will be generated before implementation.
- `CLI MVP and Simplicity`: Pass. The refactor remains entirely inside the
  existing CLI pipeline and adds no new interface surface.
- `Modular Comic Pipeline`: Pass. The feature tightens the story-planning
  module boundary without changing provider, layout, export, or safety stages.
- `Verifiable Core Logic`: Pass. The new planning behavior is deterministic and
  will be covered with `pytest` unit tests and mock-safe pipeline checks.
- `Minimal Provider Abstraction`: Pass. Provider behavior remains untouched and
  no new provider abstraction is introduced.
- `Character and Style Consistency`: Pass. The planner will produce stronger
  panel scenes while preserving downstream character and style bible usage.
- `Safety Before Generation`: Pass. Theme safety remains upstream of planning
  and planned scenes will avoid multi-panel or page-level layout instructions.
- `Real Command Verification`: Pass. Implementation will end with targeted
  planner tests and a mock-safe pipeline verification command.
- `No Speculative Features`: Pass. No external agents, live planning calls, new
  CLI arguments, or provider changes are included.
- `Documentation Stays Aligned`: Pass. README updates are conditional on
  contributor-facing architecture wording changing, and this plan tracks that.

## Project Structure

### Documentation (this feature)

```text
specs/003-story-planner-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── story-planning-contract.md
└── tasks.md
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
        ├── mock.py
        └── real_provider.py

tests/
├── integration/
│   └── test_mock_pipeline.py
└── unit/
    ├── test_prompt_builder.py
    ├── test_provider_selection.py
    ├── test_real_provider.py
    └── ...
```

**Structure Decision**: Keep the existing single-package CLI layout. The
refactor stays localized to `src/comic_agent/pipeline/story_planner.py` plus
new or updated planner-focused tests, preserving the current downstream module
boundaries.

## Consistency and Safety Design

**Character Bible**: The planner improves subject extraction quality so
downstream character bible generation receives a more stable subject anchor for
all four panels.  
**Style Bible**: The planner emits concrete scenes and avoids page-level layout
language so downstream style and prompt stages can preserve single-scene image
generation constraints.  
**Safety Strategy**: Unsafe themes continue to be rejected before generation,
and planned scene content must avoid introducing collage, grid, or multi-panel
instructions.  
**Metadata Traceability**: Existing `metadata.json` output remains unchanged in
shape, but planned panel fields will become more distinct and inspectable.  
**Documentation Traceability**: `README.md` only changes if the contributor
architecture description or workflow needs to mention `StoryPlannerAgent`.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/003-story-planner-agent/research.md) for resolved decisions on intent detection scope, subject extraction priority, deterministic panel planning, compatibility delegation, and test strategy.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/003-story-planner-agent/data-model.md)
- Story planning contract: [contracts/story-planning-contract.md](/home/caizh/programming/python_code/comic_agent/specs/003-story-planner-agent/contracts/story-planning-contract.md)
- Verification guide: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/003-story-planner-agent/quickstart.md)
- Contributor-facing contract: `README.md` at repository root if architecture wording changes

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. The design adds one internal planner
  component and no new runtime surface.
- `Modular Comic Pipeline`: Still passes. Story planning stays isolated behind
  one entrypoint and a compatibility wrapper.
- `Verifiable Core Logic`: Still passes. The design is deterministic and backed
  by intent-specific unit tests plus pipeline compatibility tests.
- `Minimal Provider Abstraction`: Still passes. Providers are unaffected.
- `Character and Style Consistency`: Still passes. Better subject extraction and
  stronger scene beats improve downstream consistency without changing bible
  ownership.
- `Safety Before Generation`: Still passes. The planner explicitly avoids
  multi-panel instructions and preserves upstream safety enforcement.
- `Documentation Stays Aligned`: Still passes. README update remains conditional
  on contributor-facing wording changes.
- `No Speculative Features`: Still passes. The supported intent set is narrow
  and rule-based by design.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
