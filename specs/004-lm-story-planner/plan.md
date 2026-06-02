# Implementation Plan: LM-assisted story planner

**Branch**: `002-real-image-provider` | **Date**: 2026-05-29 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/004-lm-story-planner/spec.md)
**Input**: Feature specification from `/specs/004-lm-story-planner/spec.md`

## Summary

Add an LM-assisted story-planning path behind a per-run CLI flag while
keeping automatic fallback to the current rule-based `StoryPlannerAgent`. The
feature validates one strict JSON storyboard result,
rejects invalid LM output, preserves the existing four-panel pipeline contract,
and keeps all automated verification mock-safe.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Standard library, Pillow, pytest, one lightweight LM client or existing HTTP-access layer for manual runs  
**Storage**: Local filesystem outputs and metadata only  
**Testing**: pytest  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Preserve the current interactive CLI workflow; LM-assisted planning should add only one bounded planning request per opted-in run  
**Constraints**: CLI-first opt-in only, existing rule-based planner remains default, strict JSON validation, automatic fallback on invalid or unavailable LM output, no external agent framework, no multi-step agent loop, preserve the `1054x1054` final comic image with `10px` `田`-shaped grid border  
**Scale/Scope**: One planning request per run, one validated LM planning result, exactly four planned panels, mock-safe automated verification only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. The feature has a completed `spec.md`, this
  `plan.md`, and will receive `tasks.md` before implementation.
- `CLI MVP and Simplicity`: Pass. The feature stays CLI-first and uses one
  explicit planner-selection flag instead of introducing broader orchestration.
- `Modular Comic Pipeline`: Pass. The design extends story planning while
  keeping prompt building, providers, composition, and export modular.
- `Verifiable Core Logic`: Pass. LM planner selection, result validation,
  fallback behavior, and metadata traceability can all be covered with mocked
  tests.
- `Minimal Provider Abstraction`: Pass. Image providers remain unchanged; the
  feature adds a planning integration, not a provider framework.
- `Character and Style Consistency`: Pass. LM-assisted planning must still feed
  the same downstream character and style consistency pipeline.
- `Safety Before Generation`: Pass. Unsafe themes remain blocked before image
  generation, and LM planning output will be rejected if it tries to produce
  page-level or multi-panel instructions.
- `Real Command Verification`: Pass. Implementation will end with targeted
  planner tests and a mock-safe pipeline verification command.
- `No Speculative Features`: Pass. The scope is intentionally limited to a
  single opt-in LM planning step plus deterministic fallback.
- `Documentation Stays Aligned`: Pass. README updates are tracked because
  planner selection and environment-based LM setup affect contributor workflow.

## Project Structure

### Documentation (this feature)

```text
specs/004-lm-story-planner/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── planner-selection-contract.md
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
    ├── test_story_planner.py
    ├── test_prompt_builder.py
    ├── test_provider_selection.py
    └── ...
```

**Structure Decision**: Keep the existing single-package CLI layout. The new
feature primarily affects planner selection and planning orchestration in
`src/comic_agent/pipeline/story_planner.py`, CLI argument handling in
`src/comic_agent/cli/generate.py`, metadata traceability, and new mocked
planner tests.

## Consistency and Safety Design

**Character Bible**: The LM-assisted planner must still provide or preserve a
subject that remains compatible with downstream character bible generation.  
**Style Bible**: LM-assisted planning must not introduce page-level layout
instructions that conflict with downstream style and prompt constraints.  
**Safety Strategy**: Unsafe themes remain upstream of planning, and LM output
validation rejects multi-panel, page-layout, or malformed panel content before
image generation proceeds.  
**Metadata Traceability**: `metadata.json` will record both the requested
planner mode and the actual planner used after any fallback.  
**Documentation Traceability**: `README.md` must document the new planner
selection flag, environment-based LM configuration, and mock-first testing
boundary.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/004-lm-story-planner/research.md) for resolved decisions on planner-selection mode, strict JSON LM output, environment-based LM configuration, fallback behavior, and mock-safe verification.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/004-lm-story-planner/data-model.md)
- Planner selection and validation contract: [contracts/planner-selection-contract.md](/home/caizh/programming/python_code/comic_agent/specs/004-lm-story-planner/contracts/planner-selection-contract.md)
- Verification guide: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/004-lm-story-planner/quickstart.md)
- Contributor and user-facing workflow contract: `README.md` at repository root

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. One CLI flag controls opt-in planner
  behavior and no broader agent surface is introduced.
- `Modular Comic Pipeline`: Still passes. LM-assisted planning is isolated to
  the planning stage and validated before prompt generation.
- `Verifiable Core Logic`: Still passes. The design relies on mocked LM
  responses and deterministic fallback behavior for tests.
- `Minimal Provider Abstraction`: Still passes. Image providers remain
  unaffected by the feature design.
- `Character and Style Consistency`: Still passes. The planner result is
  validated before it can influence downstream character and style flow.
- `Safety Before Generation`: Still passes. Invalid or multi-panel LM output is
  rejected before provider execution.
- `Documentation Stays Aligned`: Still passes. README updates are a required
  deliverable because CLI behavior and setup change.
- `No Speculative Features`: Still passes. The design intentionally excludes
  autonomous loops, external frameworks, and non-CLI surfaces.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
