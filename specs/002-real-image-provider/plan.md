# Implementation Plan: Real image provider integration

**Branch**: `002-real-image-provider` | **Date**: 2026-05-28 | **Spec**: [spec.md](/home/caizh/programming/python_code/comic_agent/specs/002-real-image-provider/spec.md)
**Input**: Feature specification from `/specs/002-real-image-provider/spec.md`

## Summary

Extend the existing four-panel comic CLI pipeline with one real text-to-image
provider behind the current provider interface, while preserving the current
story planning, prompt generation, composition, export, and metadata flow.
Credentials will be read from environment variables, configuration will be
validated before generation, automated tests will remain mock-first, and
`README.md` will be updated to document provider setup, selection, and testing
boundaries.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pillow, pytest, one real provider SDK for image generation  
**Storage**: Local filesystem outputs and metadata only  
**Testing**: pytest with mock/stubbed provider integration tests  
**Target Platform**: Local CLI execution on Linux/macOS development environments  
**Project Type**: Single-project CLI application  
**Performance Goals**: Preserve current single-run workflow and keep mock runs fast; real-provider runs should complete one four-panel request within normal interactive CLI expectations  
**Constraints**: Keep the current four-panel output contract, validate credentials before provider calls, keep MockImageProvider as the automated test default, do not add real image-to-image support, and keep README aligned with setup and provider behavior  
**Scale/Scope**: One selected real provider, one CLI request per run, exactly four generated panels, one final comic image, one metadata file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `Spec-First Delivery`: Pass. The feature has its own `spec.md`, and this
  plan defines the implementation boundary before task generation.
- `CLI MVP and Simplicity`: Pass. The change remains CLI-only and adds one real
  provider without introducing queues, web UI, or databases.
- `Modular Comic Pipeline`: Pass. The design keeps request parsing, safety,
  story planning, prompt building, provider execution, layout composition, and
  export as separate stages.
- `Verifiable Core Logic`: Pass. Provider selection, environment validation,
  metadata recording, and failure handling will be covered with `pytest` using
  stubs or mocks instead of live network calls.
- `Minimal Provider Abstraction`: Pass. The existing provider interface is
  extended surgically, with `MockImageProvider` retained as the default for
  tests and development-safe verification.
- `Character and Style Consistency`: Pass. The feature reuses the current
  prompt-building pipeline, so the generated `character_bible` and
  `style_bible` remain part of every panel prompt.
- `Safety Before Generation`: Pass. Unsafe themes and unsafe prompt guidance
  still resolve before any real provider request is made, and invalid provider
  configuration fails before generation begins.
- `Real Command Verification`: Pass. Implementation will end with the smallest
  relevant test command, plus a manual mock CLI run; an additional real-provider
  smoke run is conditional on local credentials.
- `No Speculative Features`: Pass. Real image-to-image, multiple providers,
  provider registries, and advanced provider tuning stay out of scope.
- `Documentation Stays Aligned`: Pass. `README.md` is an explicit deliverable
  for setup, environment variables, provider selection, and testing boundary.

## Project Structure

### Documentation (this feature)

```text
specs/002-real-image-provider/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── tasks.md

README.md               # User-facing provider setup and usage contract
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
    ├── test_provider_selection.py
    ├── test_provider_config.py
    ├── test_prompt_builder.py
    ├── test_reference_image_validation.py
    ├── test_layout_composer.py
    └── test_metadata_export.py
```

**Structure Decision**: Keep the existing single-package CLI layout and add one
real-provider module under `src/comic_agent/providers/`. This preserves the
current pipeline and limits the change surface to provider selection, provider
configuration, metadata, tests, and README updates.

## Consistency and Safety Design

**Character Bible**: The current request-level `character_bible` remains
generated in the prompt-building stage and is passed unchanged into every panel
prompt, regardless of provider mode.  
**Style Bible**: The current request-level `style_bible` remains generated once
per run and injected into every panel prompt before provider execution.  
**Safety Strategy**: Theme rejection and prompt-sanitization continue to happen
before provider selection executes any image generation call. Real provider
configuration validation also happens before the first external request.  
**Metadata Traceability**: `metadata.json` will keep existing request, story,
prompt, output-path, and warning fields, and will be extended with provider
name, provider mode, retry counts, and provider failure details when available.  
**Documentation Traceability**: `README.md` must describe provider setup,
environment variables, provider selection, mock-first testing, and the continued
absence of real image-to-image support.

## Phase 0: Research Summary

See [research.md](/home/caizh/programming/python_code/comic_agent/specs/002-real-image-provider/research.md) for resolved decisions on provider selection, environment-based credential validation, text-to-image-only scope, metadata extension, and mock-first testing strategy.

## Phase 1: Design Outputs

- Data model: [data-model.md](/home/caizh/programming/python_code/comic_agent/specs/002-real-image-provider/data-model.md)
- CLI contract: [contracts/cli-contract.md](/home/caizh/programming/python_code/comic_agent/specs/002-real-image-provider/contracts/cli-contract.md)
- Validation flow and smoke-run steps: [quickstart.md](/home/caizh/programming/python_code/comic_agent/specs/002-real-image-provider/quickstart.md)
- Contributor and user-facing contract: `README.md` at repository root

## Post-Design Constitution Check

- `CLI MVP and Simplicity`: Still passes. One real provider is added without
  changing the project shape.
- `Modular Comic Pipeline`: Still passes. Provider execution is the only stage
  materially extended, and upstream/downstream modules preserve their roles.
- `Verifiable Core Logic`: Still passes. The design keeps tests mock-first and
  targets the new provider behavior with stubs and isolated checks.
- `Minimal Provider Abstraction`: Still passes. The provider boundary remains a
  small interface with one mock and one real implementation.
- `Character and Style Consistency`: Still passes. Existing bibles and prompt
  construction remain the source of panel consistency.
- `Safety Before Generation`: Still passes. Safety and config validation both
  happen before real provider execution.
- `Documentation Stays Aligned`: Still passes. README updates are a first-class
  output of this feature.
- `No Speculative Features`: Still passes. Deferred scope remains explicit.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
