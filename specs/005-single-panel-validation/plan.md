# Implementation Plan: Single-panel generation validation and retry

**Branch**: `002-real-image-provider` | **Date**: 2026-05-29 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/005-single-panel-validation/spec.md)
**Input**: Feature specification from `/specs/005-single-panel-validation/spec.md`

## Summary

Add a post-generation single-panel validation boundary and bounded retry
strategies to the comic pipeline so invalid nested multi-panel or storyboard
images are rejected before composition. The design preserves one-provider-call
per panel attempt, keeps the existing final `1054x1054` layout unchanged,
records per-attempt validation and retry traceability in metadata, and keeps
automated verification mock-safe.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Standard library, Pillow, pytest, existing mock and Wanx provider code  
**Storage**: Local filesystem outputs and metadata only  
**Testing**: pytest  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Preserve the current interactive CLI workflow while
adding only one bounded validation check per panel attempt and bounded retries
only when validation fails  
**Constraints**: Preserve current provider interfaces where possible, preserve
the `1054x1054` final comic image with `10px` `田`-shaped grid border, avoid
network requirements in automated tests, keep retry deterministic and bounded,
and avoid external agent frameworks  
**Scale/Scope**: One validation decision per panel attempt, one accepted panel
artifact per panel, bounded per-panel retries, mock-safe verification only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. The feature has a completed `spec.md`, this
  `plan.md`, and will receive `tasks.md` before implementation.
- `CLI MVP and Simplicity`: Pass. The feature stays CLI-first and adds a
  bounded validation and retry loop rather than a larger orchestration system.
- `Modular Comic Pipeline`: Pass. The design keeps story planning, prompt
  building, provider execution, panel validation, composition, and export as
  separable stages.
- `Verifiable Core Logic`: Pass. Validation, retry progression, retry
  exhaustion, and metadata traceability are all mockable and deterministic in
  tests.
- `Minimal Provider Abstraction`: Pass. Providers remain responsible for image
  generation, while panel acceptance logic is added as a separate validation
  boundary rather than expanding provider scope.
- `Character and Style Consistency`: Pass. Character and style bibles remain
  upstream inputs to prompt generation, and retry strategies only change how
  one panel attempt is requested, not the underlying character/style contract.
- `Safety Before Generation`: Pass. Unsafe themes continue to be rejected
  before provider execution, and invalid images are rejected before final
  composition.
- `Real Command Verification`: Pass. Implementation will end with targeted
  mock-safe tests and `python3 -m compileall src tests`.
- `No Speculative Features`: Pass. The scope is intentionally limited to
  validation, retry, metadata traceability, and contributor documentation.
- `Documentation Stays Aligned`: Pass. README updates are required because
  debugging and run traceability expectations will change.

## Project Structure

### Documentation (this feature)

```text
specs/005-single-panel-validation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── single-panel-validation-contract.md
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
    │   ├── comic_request.py
    │   ├── metadata.py
    │   └── panel.py
    ├── pipeline/
    │   ├── story_planner.py
    │   ├── prompt_builder.py
    │   ├── composer.py
    │   ├── exporter.py
    │   └── safety.py
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
    ├── test_metadata_export.py
    ├── test_real_provider.py
    └── ...
```

**Structure Decision**: Keep the existing single-package CLI layout. The new
feature primarily affects generation orchestration in
`src/comic_agent/cli/generate.py`, metadata traceability, and a new validation
boundary in the pipeline layer, with supporting mocked tests.

## Consistency and Safety Design

**Character Bible**: Character bible generation remains unchanged and continues
to define subject appearance consistency before any panel attempt is generated.  
**Style Bible**: Style bible generation remains unchanged and continues to
provide stable rendering direction across attempts. Retry strategies may alter
prompt strictness but must not alter the base style contract.  
**Safety Strategy**: Unsafe themes remain rejected before any provider attempt.
Single-panel validation is an output-quality gate, not a replacement for safety
filtering.  
**Metadata Traceability**: `metadata.json` will record panel-attempt strategy,
validation decision, rejection reason, and final accepted-or-failed status for
each panel.  
**Validation Boundary**: Image generation and image acceptance become separate
stages. A provider can succeed while a panel attempt is still rejected by the
single-panel validator.  
**Documentation Traceability**: `README.md` must document the new validation and
retry behavior and how to interpret metadata for rejected or retried panels.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/005-single-panel-validation/research.md) for resolved decisions on validator architecture, retry strategy progression, metadata shape, and mock-safe verification.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/005-single-panel-validation/data-model.md)
- Validation and retry contract: [contracts/single-panel-validation-contract.md](/home/caizh/programming/python_code/comic_agent/specs/005-single-panel-validation/contracts/single-panel-validation-contract.md)
- Verification guide: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/005-single-panel-validation/quickstart.md)
- Contributor and user-facing workflow contract: `README.md` at repository root

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. Validation and retry remain internal
  pipeline concerns and do not introduce a new product surface by default.
- `Modular Comic Pipeline`: Still passes. Validation is isolated as a separate
  boundary rather than pushed into provider or prompt-builder responsibilities.
- `Verifiable Core Logic`: Still passes. Validation outcomes, retry steps, and
  failure exhaustion can all be simulated without network access.
- `Minimal Provider Abstraction`: Still passes. Providers still return image
  data; they do not decide whether an image satisfies the single-panel contract.
- `Character and Style Consistency`: Still passes. Validation and retry reuse
  the same upstream consistency inputs.
- `Safety Before Generation`: Still passes. Unsafe themes are still blocked
  before any provider attempt begins.
- `Documentation Stays Aligned`: Still passes. README updates remain a tracked
  deliverable because runtime debugging expectations change.
- `No Speculative Features`: Still passes. The design excludes image editing,
  background workflows, and provider expansion.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
