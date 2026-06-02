# Tasks: Single-panel generation validation and retry

**Input**: Design documents from `/specs/005-single-panel-validation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include test tasks whenever the feature changes core logic. External
provider interactions MUST be covered with mocked tests rather than live API
calls unless the spec explicitly requires a real-provider verification step.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g. [US1], [US2], [US3])
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths below assume the current single-project CLI layout from `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture the new validation-and-retry scope and prepare task-specific test files.

- [x] T001 Create single-panel validation test module scaffold in `tests/unit/test_panel_validation.py`
- [x] T002 Review validation, retry, metadata, and compatibility requirements in `specs/005-single-panel-validation/spec.md`, `specs/005-single-panel-validation/contracts/single-panel-validation-contract.md`, and `specs/005-single-panel-validation/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared validator, retry strategy, and metadata structures required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Define panel-attempt, validator, and retry-strategy boundaries in `src/comic_agent/models/metadata.py`, `src/comic_agent/models/panel.py`, and `src/comic_agent/cli/generate.py`
- [x] T004 [P] Add foundational tests for single-panel validator decisions in `tests/unit/test_panel_validation.py`
- [x] T005 [P] Add foundational tests for per-attempt metadata serialization in `tests/unit/test_metadata_export.py`
- [x] T006 [P] Add foundational tests for bounded retry strategy selection in `tests/unit/test_panel_validation.py`
- [x] T007 Implement shared panel-attempt trace models and metadata serialization in `src/comic_agent/models/metadata.py` and `src/comic_agent/pipeline/exporter.py`
- [x] T008 Implement validator and retry-strategy scaffolding in `src/comic_agent/pipeline/panel_validation.py`
- [x] T009 Wire generation orchestration to separate provider success from panel acceptance in `src/comic_agent/cli/generate.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Reject Broken Single-Panel Images (Priority: P1) 🎯 MVP

**Goal**: Automatically reject generated images that do not satisfy the single-panel contract before they reach final composition.

**Independent Test**: Simulate valid and invalid panel attempts and verify that invalid nested or subdivided images are not silently accepted as successful panels.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Add validator acceptance/rejection tests for nested multi-panel and valid single-scene cases in `tests/unit/test_panel_validation.py`
- [x] T011 [P] [US1] Add generation-flow tests that reject provider-successful but validator-failed panels in `tests/unit/test_provider_selection.py`

### Implementation for User Story 1

- [x] T012 [US1] Implement concrete single-panel validator rules and decision reasons in `src/comic_agent/pipeline/panel_validation.py`
- [x] T013 [US1] Integrate validator execution after each provider attempt in `src/comic_agent/cli/generate.py`
- [x] T014 [US1] Record validator rejection outcomes on panel records in `src/comic_agent/models/panel.py` and `src/comic_agent/models/metadata.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Retry with Stronger Generation Strategies (Priority: P2)

**Goal**: Retry validator-rejected panel attempts with deterministic stronger single-scene strategies before declaring the panel failed.

**Independent Test**: Simulate one rejected first attempt followed by one accepted later attempt, and verify bounded retry progression and final accepted-attempt traceability.

### Tests for User Story 2 ⚠️

- [x] T015 [P] [US2] Add retry progression and retry exhaustion tests in `tests/unit/test_panel_validation.py`
- [x] T016 [P] [US2] Add generation-flow tests for validator-triggered retries in `tests/unit/test_provider_selection.py`
- [x] T017 [P] [US2] Add metadata tests for accepted-attempt and exhausted-attempt traces in `tests/unit/test_metadata_export.py`

### Implementation for User Story 2

- [x] T018 [US2] Implement deterministic retry strategy profiles and bounded progression in `src/comic_agent/pipeline/panel_validation.py`
- [x] T019 [US2] Apply strategy-specific prompt or attempt adjustments during retries in `src/comic_agent/cli/generate.py` and `src/comic_agent/pipeline/prompt_builder.py`
- [x] T020 [US2] Record accepted attempt number, final failure reason, and strategy usage in `src/comic_agent/models/metadata.py` and `src/comic_agent/pipeline/exporter.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Preserve Stable Pipeline Contracts (Priority: P3)

**Goal**: Keep CLI behavior, provider behavior, final layout, and mock-safe pipeline compatibility stable while validation and retry are introduced.

**Independent Test**: Run mocked pipeline coverage and confirm that successful runs still produce four accepted panel artifacts, a final `1054x1054` comic, and readable metadata with attempt traces.

### Tests for User Story 3 ⚠️

- [x] T021 [P] [US3] Update prompt-builder compatibility assertions for retry-aware prompt generation in `tests/unit/test_prompt_builder.py`
- [x] T022 [P] [US3] Update mock pipeline coverage for accepted, retried, and failed panel traces in `tests/integration/test_mock_pipeline.py`
- [x] T023 [P] [US3] Add provider-message compatibility assertions if retry strategies affect provider-facing prompts in `tests/unit/test_real_provider.py`

### Implementation for User Story 3

- [x] T024 [US3] Preserve final composition input contract and accepted-panel-only flow in `src/comic_agent/cli/generate.py` and `src/comic_agent/pipeline/composer.py`
- [x] T025 [US3] Keep mock and Wanx provider interfaces unchanged while validation and retry remain external to providers in `src/comic_agent/providers/base.py`, `src/comic_agent/providers/mock.py`, and `src/comic_agent/providers/real_provider.py`
- [x] T026 [US3] Update contributor and user workflow documentation for validation, retries, and metadata interpretation in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cross-story cleanup

- [x] T027 [P] Review validator rejection coverage against `specs/005-single-panel-validation/contracts/single-panel-validation-contract.md`
- [ ] T028 Run targeted mock-safe verification commands from `specs/005-single-panel-validation/quickstart.md`
- [x] T029 [P] Run `python3 -m compileall src tests` and document any environment limitations in implementation notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - establishes the validator boundary and rejection flow
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - builds on validator and metadata scaffolding to add retries
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - validates downstream compatibility once validator and retry behavior exist

### Within Each User Story

- Tests for changed core logic MUST be written and FAIL before implementation
- Validator decisions before retry orchestration
- Retry orchestration before metadata completion
- Accepted-panel-only flow before final compatibility signoff

### Parallel Opportunities

- T004, T005, and T006 can run in parallel after T003
- T010 and T011 can run in parallel
- T015, T016, and T017 can run in parallel
- T021, T022, and T023 can run in parallel
- T027 and T029 can run in parallel during polish

---

## Parallel Example: User Story 2

```bash
# Launch all retry tests for User Story 2 together:
Task: "Add retry progression and retry exhaustion tests in tests/unit/test_panel_validation.py"
Task: "Add generation-flow tests for validator-triggered retries in tests/unit/test_provider_selection.py"
Task: "Add metadata tests for accepted-attempt and exhausted-attempt traces in tests/unit/test_metadata_export.py"

# Launch all User Story 3 compatibility tests together:
Task: "Update prompt-builder compatibility assertions for retry-aware prompt generation in tests/unit/test_prompt_builder.py"
Task: "Update mock pipeline coverage for accepted, retried, and failed panel traces in tests/integration/test_mock_pipeline.py"
Task: "Add provider-message compatibility assertions if retry strategies affect provider-facing prompts in tests/unit/test_real_provider.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm invalid nested multi-panel outputs are rejected before composition
5. Demo the validator boundary before adding retry complexity

### Incremental Delivery

1. Complete Setup + Foundational → validator, retry, and metadata foundations ready
2. Add User Story 1 → test independently → validator-based rejection available
3. Add User Story 2 → test independently → bounded retry recovery available
4. Add User Story 3 → test independently → downstream compatibility preserved
5. Finish with polish verification commands

### Parallel Team Strategy

With multiple developers:

1. One developer completes Foundational validator and metadata scaffolding
2. After Foundational is done:
   - Developer A: User Story 1 validator decisions and rejection flow
   - Developer B: User Story 2 retry progression and metadata traceability
   - Developer C: User Story 3 compatibility tests and documentation

---

## Notes

- [P] tasks = different files, no dependencies
- [US1], [US2], [US3] labels map tasks directly to prioritized user stories
- Each user story remains independently testable
- Validation outcomes and retry paths should be mocked in automated verification
- Avoid changing provider responsibilities unless compatibility wiring strictly requires it
