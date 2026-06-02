# Tasks: LM-assisted story planner

**Input**: Design documents from `/specs/004-lm-story-planner/`
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

- **Single project**: `src/`, `tests/` at repository root
- Paths below assume the current single-project CLI layout from `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture the new planner-selection surface and set up the test files needed for LM-assisted planning coverage.

- [X] T001 Create LM-assisted planner test module scaffold in `tests/unit/test_lm_story_planner.py`
- [X] T002 Review planner-selection, validation, fallback, and metadata traceability requirements in `specs/004-lm-story-planner/spec.md`, `specs/004-lm-story-planner/contracts/planner-selection-contract.md`, and `specs/004-lm-story-planner/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared planner-selection, LM result validation, configuration, and metadata scaffolding required by every user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Define planner-selection entrypoints, LM planning boundary, and fallback orchestration shape in `src/comic_agent/pipeline/story_planner.py`
- [X] T004 [P] Add foundational tests for planner-selection mode parsing and default rule-based behavior in `tests/unit/test_lm_story_planner.py`
- [X] T005 [P] Add foundational tests for strict JSON LM payload validation rules in `tests/unit/test_lm_story_planner.py`
- [X] T006 [P] Add foundational tests for metadata traceability of requested vs actual planner mode in `tests/unit/test_metadata_export.py`
- [X] T007 Implement shared planner-selection parsing, strict JSON validation helpers, and fallback triggers in `src/comic_agent/pipeline/story_planner.py`
- [X] T008 Implement environment-based LM configuration validation for manual runs in `src/comic_agent/pipeline/story_planner.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Opt Into LM-Assisted Planning (Priority: P1) 🎯 MVP

**Goal**: Let users explicitly enable LM-assisted planning per run while keeping the rule-based planner as the default.

**Independent Test**: Run story-planning tests with planner mode explicitly set to LM-assisted and verify the system attempts the LM path, validates the response, and still returns a valid four-panel story structure.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add CLI parsing test for explicit planner-selection flag in `tests/unit/test_provider_selection.py`
- [X] T010 [P] [US1] Add unit test for successful LM-assisted planning conversion into `StoryStructure` in `tests/unit/test_lm_story_planner.py`

### Implementation for User Story 1

- [X] T011 [US1] Add the per-run planner-selection CLI flag and request plumbing in `src/comic_agent/cli/generate.py`
- [X] T012 [US1] Extend `ComicRequest` to carry planner-selection mode in `src/comic_agent/models/comic_request.py`
- [X] T013 [US1] Implement LM-assisted planner selection and validated story conversion in `src/comic_agent/pipeline/story_planner.py`
- [X] T014 [US1] Preserve downstream prompt-building compatibility for successful LM-assisted planning in `src/comic_agent/pipeline/prompt_builder.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Fallback Safely on LM Failure (Priority: P2)

**Goal**: Fall back automatically to the rule-based planner when LM-assisted planning is invalid, unavailable, or rejected.

**Independent Test**: Simulate malformed JSON, missing fields, invalid panel counts, planner unavailability, and timeouts, and verify the system falls back to the rule-based planner while preserving a valid four-panel output contract.

### Tests for User Story 2 ⚠️

- [X] T015 [P] [US2] Add malformed JSON and schema-failure fallback tests in `tests/unit/test_lm_story_planner.py`
- [X] T016 [P] [US2] Add unavailability and timeout fallback tests in `tests/unit/test_lm_story_planner.py`
- [X] T017 [P] [US2] Add explicit-character conflict rejection test in `tests/unit/test_lm_story_planner.py`

### Implementation for User Story 2

- [X] T018 [US2] Implement automatic fallback from LM-assisted planning to rule-based planning in `src/comic_agent/pipeline/story_planner.py`
- [X] T019 [US2] Enforce subject-authority and single-scene rejection rules for LM payloads in `src/comic_agent/pipeline/story_planner.py`
- [X] T020 [US2] Record fallback reason and actual planner mode in metadata structures in `src/comic_agent/models/metadata.py` and `src/comic_agent/pipeline/exporter.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Keep Tests and Pipeline Behavior Stable (Priority: P3)

**Goal**: Preserve mock-safe tests and unchanged downstream prompt, provider, metadata, and final layout contracts.

**Independent Test**: Run mocked planner and mock pipeline verification to confirm LM-assisted or fallback planning still feeds the same prompt-generation, provider, and composition contracts.

### Tests for User Story 3 ⚠️

- [X] T021 [P] [US3] Update prompt-builder compatibility assertions for LM-assisted and fallback story structures in `tests/unit/test_prompt_builder.py`
- [X] T022 [P] [US3] Add metadata assertions for requested and actual planner mode in `tests/unit/test_metadata_export.py`
- [X] T023 [P] [US3] Update mock pipeline coverage for planner-selection compatibility in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 3

- [X] T024 [US3] Preserve `StoryStructure` output compatibility for prompt generation and providers in `src/comic_agent/pipeline/story_planner.py`
- [X] T025 [US3] Keep mock and Wanx provider behavior unchanged while integrating planner selection in `src/comic_agent/cli/generate.py`
- [X] T026 [US3] Update contributor and user workflow documentation for planner selection and LM setup in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cross-story cleanup

- [X] T027 [P] Review LM payload rejection rules against `specs/004-lm-story-planner/contracts/planner-selection-contract.md` to ensure invalid page-layout or multi-panel content always falls back safely
- [ ] T028 Run targeted mock-safe verification commands from `specs/004-lm-story-planner/quickstart.md`
- [X] T029 [P] Run `python3 -m compileall src tests` and document any environment limitations in implementation notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - establishes the opt-in LM-assisted path
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - builds on planner selection and validation scaffolding
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - validates downstream compatibility after US1 and US2 behavior exists

### Within Each User Story

- Tests for changed core logic MUST be written and FAIL before implementation
- Planner selection and request plumbing before fallback and metadata integration
- Validation before live LM-assisted planning acceptance
- Fallback behavior before downstream compatibility signoff

### Parallel Opportunities

- T004, T005, and T006 can run in parallel after T003
- T009 and T010 can run in parallel
- T015, T016, and T017 can run in parallel
- T021, T022, and T023 can run in parallel
- T027 and T029 can run in parallel during polish

---

## Parallel Example: User Story 2

```bash
# Launch all fallback tests for User Story 2 together:
Task: "Add malformed JSON and schema-failure fallback tests in tests/unit/test_lm_story_planner.py"
Task: "Add unavailability and timeout fallback tests in tests/unit/test_lm_story_planner.py"
Task: "Add explicit-character conflict rejection test in tests/unit/test_lm_story_planner.py"

# Launch all User Story 3 downstream compatibility tests together:
Task: "Update prompt-builder compatibility assertions for LM-assisted and fallback story structures in tests/unit/test_prompt_builder.py"
Task: "Add metadata assertions for requested and actual planner mode in tests/unit/test_metadata_export.py"
Task: "Update mock pipeline coverage for planner-selection compatibility in tests/integration/test_mock_pipeline.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm the explicit planner-selection flag enables LM-assisted planning while the default remains rule-based
5. Demo the opt-in behavior before adding fallback complexity

### Incremental Delivery

1. Complete Setup + Foundational → planner-selection and validation foundation ready
2. Add User Story 1 → test independently → opt-in LM-assisted path available
3. Add User Story 2 → test independently → fallback safety and metadata traceability complete
4. Add User Story 3 → test independently → downstream compatibility preserved
5. Finish with polish verification commands

### Parallel Team Strategy

With multiple developers:

1. One developer completes Foundational planner-selection and validation scaffolding
2. After Foundational is done:
   - Developer A: User Story 1 CLI flag and request plumbing
   - Developer B: User Story 2 fallback and metadata traceability
   - Developer C: User Story 3 downstream compatibility tests and documentation

---

## Notes

- [P] tasks = different files, no dependencies
- [US1], [US2], [US3] labels map tasks directly to prioritized user stories
- Each user story remains independently testable
- Mock LM responses should be used everywhere in automated verification
- Avoid changing provider logic or final layout behavior unless compatibility wiring strictly requires it
