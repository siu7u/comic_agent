# Tasks: Four-panel comic generation MVP

**Input**: Design documents from `/specs/001-four-panel-comic/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include test tasks whenever the feature changes core logic. External
provider interactions MUST be covered with mocked tests rather than live API
calls unless the spec explicitly requires a real-provider verification step.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/`, `README.md` at repository root
- Paths shown below assume the structure defined in `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create the package and test directory structure in `src/comic_agent/`, `tests/unit/`, and `tests/integration/`
- [X] T002 Create Python package entry files in `src/comic_agent/__init__.py`, `src/comic_agent/cli/__init__.py`, `src/comic_agent/models/__init__.py`, `src/comic_agent/pipeline/__init__.py`, and `src/comic_agent/providers/__init__.py`
- [X] T003 [P] Create the CLI entrypoint stub for `comic-agent generate` in `src/comic_agent/cli/generate.py`
- [X] T004 [P] Add a package metadata and dependency manifest for Python 3.11+, Pillow, and pytest in `pyproject.toml`
- [X] T005 [P] Create the initial user-facing project contract in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Define shared request, bible, panel, metadata, and documentation-deliverable models in `src/comic_agent/models/comic_request.py`, `src/comic_agent/models/bibles.py`, `src/comic_agent/models/panel.py`, and `src/comic_agent/models/metadata.py`
- [X] T007 [P] Implement request parsing and reference-image validation helpers in `src/comic_agent/cli/generate.py`
- [X] T008 [P] Implement safety policy helpers for theme rejection and prompt rewrite decisions in `src/comic_agent/pipeline/safety.py`
- [X] T009 [P] Define the provider interface in `src/comic_agent/providers/base.py`
- [X] T010 [P] Implement deterministic `MockImageProvider` scaffolding in `src/comic_agent/providers/mock.py`
- [X] T011 Implement shared metadata export helpers and output-path conventions in `src/comic_agent/pipeline/exporter.py`
- [X] T012 Implement README synchronization checkpoints for setup, CLI, outputs, provider boundary, and test commands in `README.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate a complete comic (Priority: P1) 🎯 MVP

**Goal**: Accept a theme-driven request and produce a complete four-panel comic
package with story structure, panel images, final comic image, metadata, and
aligned user-facing documentation.

**Independent Test**: Run `comic-agent generate --theme "<idea>" --out <dir>`
and confirm four panel PNGs, `comic.png`, and `metadata.json` are created with
the fixed sizes and four-panel structure, then confirm `README.md` describes the
base CLI flow and output files.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add unit tests for prompt generation and fixed four-panel story output in `tests/unit/test_prompt_builder.py`
- [X] T014 [P] [US1] Add unit tests for 1054x1054 composition and panel placement in `tests/unit/test_layout_composer.py`
- [X] T015 [P] [US1] Add integration tests for the end-to-end mock pipeline in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement story planning for exactly four ordered panels in `src/comic_agent/pipeline/story_planner.py`
- [X] T017 [P] [US1] Implement panel prompt generation with shared bible injection in `src/comic_agent/pipeline/prompt_builder.py`
- [X] T018 [US1] Implement mock panel image generation with retry handling in `src/comic_agent/providers/mock.py`
- [X] T019 [US1] Implement fixed-canvas 2x2 comic composition in `src/comic_agent/pipeline/composer.py`
- [X] T020 [US1] Implement artifact export for panel PNGs, `comic.png`, and `metadata.json` in `src/comic_agent/pipeline/exporter.py`
- [X] T021 [US1] Wire the CLI end-to-end generation flow in `src/comic_agent/cli/generate.py`
- [X] T022 [US1] Document base installation, CLI usage, expected outputs, and module responsibilities in `README.md`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Guide panel visuals (Priority: P2)

**Goal**: Allow users to steer prompt generation with global guidance,
per-panel prompt input, and one validated reference image while preserving story
structure, prompt consistency, and aligned contributor documentation.

**Independent Test**: Run the CLI with `--image-prompt`, one or more
`--panel-prompt-*` flags, and `--reference-image`, then confirm missing panel
prompts are generated, provided guidance is merged, metadata records prompt
sources and reference-image usage, and `README.md` documents the guided input
contract.

### Tests for User Story 2 ⚠️

- [X] T023 [P] [US2] Add unit tests for prompt-source merging and missing-panel prompt generation in `tests/unit/test_prompt_builder.py`
- [X] T024 [P] [US2] Add unit tests for reference-image path validation and request normalization in `tests/unit/test_reference_image_validation.py`
- [X] T025 [P] [US2] Extend integration coverage for guided prompt and reference-image runs in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 2

- [X] T026 [P] [US2] Extend request and panel metadata models for prompt-source tracking and reference-image fields in `src/comic_agent/models/comic_request.py`, `src/comic_agent/models/panel.py`, and `src/comic_agent/models/metadata.py`
- [X] T027 [US2] Implement global/per-panel prompt merge behavior and missing-panel prompt generation in `src/comic_agent/pipeline/prompt_builder.py`
- [X] T028 [US2] Extend CLI argument handling for `--image-prompt`, `--panel-prompt-1` through `--panel-prompt-4`, and `--reference-image` in `src/comic_agent/cli/generate.py`
- [X] T029 [US2] Export prompt sources and reference-image metadata in `src/comic_agent/pipeline/exporter.py`
- [X] T030 [US2] Update guided-prompt, reference-image, and metadata documentation in `README.md`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Receive safe and transparent adjustments (Priority: P3)

**Goal**: Reject unsafe requests early, minimally rewrite conflicting prompt
guidance, record all safety outcomes in metadata, and explain those user-visible
behaviors in README.

**Independent Test**: Run the CLI with unsafe theme input and with conflicting
prompt guidance, then confirm unsafe themes are rejected before story planning,
prompt rewrites are recorded in metadata, and `README.md` explains the MVP
safety and provider boundaries.

### Tests for User Story 3 ⚠️

- [X] T031 [P] [US3] Add unit tests for unsafe theme rejection and prompt rewrite decisions in `tests/unit/test_prompt_builder.py`
- [X] T032 [P] [US3] Add unit tests for warning and rewrite metadata export in `tests/unit/test_metadata_export.py`
- [X] T033 [P] [US3] Extend integration coverage for rejection and rewritten-guidance flows in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 3

- [X] T034 [P] [US3] Implement theme-level rejection and prompt rewrite policy in `src/comic_agent/pipeline/safety.py`
- [X] T035 [US3] Integrate safety gating into story planning and prompt finalization in `src/comic_agent/pipeline/story_planner.py` and `src/comic_agent/pipeline/prompt_builder.py`
- [X] T036 [US3] Persist warnings, rewritten prompts, and retry outcomes in `src/comic_agent/pipeline/exporter.py` and `src/comic_agent/models/metadata.py`
- [X] T037 [US3] Surface clear CLI error messages for rejected themes and invalid guidance in `src/comic_agent/cli/generate.py`
- [X] T038 [US3] Update README safety, provider-boundary, and test-run sections in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Align `specs/001-four-panel-comic/quickstart.md` with the final install command, CLI examples, and verification commands
- [X] T040 [P] Review `README.md` against the current CLI contract, output files, metadata behavior, provider boundary, and test commands in `specs/001-four-panel-comic/contracts/cli-contract.md`
- [X] T041 Run the smallest relevant real verification command for the MVP, such as `pytest tests/integration/test_mock_pipeline.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel if needed
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on the P1 pipeline but remains independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with prompt-building, export, and documentation behavior from US1/US2

### Within Each User Story

- Tests for changed core logic MUST be written and FAIL before implementation
- Shared models before pipeline integration when the model shape changes
- Prompt-building and safety updates before provider execution changes
- Export and CLI wiring after core logic is in place
- README updates in the same story phase whenever user-facing behavior changes
- Story complete before moving to the next priority if shipping incrementally

### Parallel Opportunities

- `T003`, `T004`, and `T005` can run in parallel after the repository structure is confirmed
- `T007` through `T010` can run in parallel within the foundational phase
- `T013`, `T014`, and `T015` can run in parallel for US1
- `T023`, `T024`, and `T025` can run in parallel for US2
- `T031`, `T032`, and `T033` can run in parallel for US3
- `T039` and `T040` can run in parallel during polish

---

## Parallel Example: User Story 2

```bash
# Launch all US2 test tasks together:
Task: "Add unit tests for prompt-source merging and missing-panel prompt generation in tests/unit/test_prompt_builder.py"
Task: "Add unit tests for reference-image path validation and request normalization in tests/unit/test_reference_image_validation.py"
Task: "Extend integration coverage for guided prompt and reference-image runs in tests/integration/test_mock_pipeline.py"

# Launch independent implementation/documentation tasks after shared models exist:
Task: "Implement global/per-panel prompt merge behavior and missing-panel prompt generation in src/comic_agent/pipeline/prompt_builder.py"
Task: "Update guided-prompt, reference-image, and metadata documentation in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the US1 integration test and a CLI demo
5. Review generated artifacts and README coverage together

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Review outputs and README
3. Add User Story 2 → Test independently → Review guided prompt behavior and README
4. Add User Story 3 → Test independently → Review safety/metadata behavior and README
5. Finish with the smallest relevant verification command

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 core pipeline
   - Developer B: User Story 2 prompt and reference-image behavior
   - Developer C: User Story 3 safety, metadata transparency, and README synchronization
3. Merge only after each story passes its own tests and documentation checks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- All tasks include exact file paths
- README creation is an explicit implementation task
- Future user-facing behavior changes must include same-change README updates
- Suggested MVP scope is Phase 1 + Phase 2 + Phase 3 (User Story 1)
