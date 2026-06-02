# Tasks: StoryPlannerAgent refactor

**Input**: Design documents from `/specs/003-story-planner-agent/`
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

**Purpose**: Capture the feature surface and create the shared test location for planner coverage.

- [X] T001 Create planner-focused test module scaffold in `tests/unit/test_story_planner.py`
- [X] T002 Review and align story-planning requirements, contract expectations, and verification themes in `specs/003-story-planner-agent/spec.md`, `specs/003-story-planner-agent/contracts/story-planning-contract.md`, and `specs/003-story-planner-agent/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the internal planner boundary and shared subject/intent infrastructure required by every user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Define `StoryPlannerAgent` entrypoint, planning context helpers, and compatibility delegation shape in `src/comic_agent/pipeline/story_planner.py`
- [X] T004 [P] Add foundational unit tests for subject extraction priority and action-phrase trimming in `tests/unit/test_story_planner.py`
- [X] T005 [P] Add foundational unit tests for deterministic intent detection priority and fallback selection in `tests/unit/test_story_planner.py`
- [X] T006 Implement normalized subject extraction and single-intent selection utilities in `src/comic_agent/pipeline/story_planner.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Plan Stronger Visual Stories (Priority: P1) 🎯 MVP

**Goal**: Replace repetitive template scenes with four concrete, distinct visual story beats for ordinary CLI themes.

**Independent Test**: Run planner tests for `一只小兔子上学的一天` and verify exactly four distinct panels with captions `Morning`, `On the Way`, `At School`, and `Going Home`, covering departure, journey, school activity, and return or end-of-day resolution.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add regression test for `一只小兔子上学的一天` planning output in `tests/unit/test_story_planner.py`
- [X] T008 [P] [US1] Add unit test for concrete fallback scene distinctness in `tests/unit/test_story_planner.py`

### Implementation for User Story 1

- [X] T009 [US1] Implement school-day planning beats, captions, and concrete scene generation in `src/comic_agent/pipeline/story_planner.py`
- [X] T010 [US1] Implement stronger fallback gag-comic scene generation with distinct panel-level actions and visuals in `src/comic_agent/pipeline/story_planner.py`
- [X] T011 [US1] Ensure planned panels avoid page-level layout and multi-panel instructions in `src/comic_agent/pipeline/story_planner.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Detect Common Story Intents (Priority: P2)

**Goal**: Support deterministic seasonal and journey-or-growth planning modes with concrete, stage-specific scenes.

**Independent Test**: Run planner tests for the seasonal regression theme and one journey/growth theme, and verify captions and scene progression match the selected intent without combining multiple stages in one panel.

### Tests for User Story 2 ⚠️

- [X] T012 [P] [US2] Add regression test for `记录同一只流浪橘猫在四季中的变化，特征保持一致` in `tests/unit/test_story_planner.py`
- [X] T013 [P] [US2] Add unit test for journey or growth progression planning in `tests/unit/test_story_planner.py`

### Implementation for User Story 2

- [X] T014 [US2] Implement seasonal progression planning beats with `Spring`, `Summer`, `Autumn`, and `Winter` captions in `src/comic_agent/pipeline/story_planner.py`
- [X] T015 [US2] Implement journey or transformation or growth planning beats with `Beginning`, `Challenge`, `Change`, and `Result` captions in `src/comic_agent/pipeline/story_planner.py`
- [X] T016 [US2] Enforce one-stage-per-panel scene rules for seasonal and progression planning in `src/comic_agent/pipeline/story_planner.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Preserve Pipeline Compatibility (Priority: P3)

**Goal**: Keep the refactor compatible with prompt generation, metadata export, and mock-safe CLI pipeline behavior.

**Independent Test**: Run compatibility tests showing `build_story_structure(request)` still returns a valid four-panel `StoryStructure` consumed by prompt-building and mock pipeline flows without network access.

### Tests for User Story 3 ⚠️

- [X] T017 [P] [US3] Add compatibility test for `build_story_structure(request)` delegation in `tests/unit/test_story_planner.py`
- [X] T018 [P] [US3] Update prompt-building assertions for planner-produced concrete scenes in `tests/unit/test_prompt_builder.py`
- [X] T019 [P] [US3] Update mock pipeline verification for planner compatibility in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 3

- [X] T020 [US3] Wire `build_story_structure(request)` to delegate through the new internal planner entrypoint in `src/comic_agent/pipeline/story_planner.py`
- [X] T021 [US3] Preserve current `StoryStructure` and `PanelSpec` field population for downstream prompt and metadata consumers in `src/comic_agent/pipeline/story_planner.py`
- [X] T022 [US3] Update contributor-facing architecture notes only if needed in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup across all stories

- [X] T023 [P] Review planner wording against `specs/003-story-planner-agent/contracts/story-planning-contract.md` to ensure no scene introduces collage or page-level layout language
- [X] T024 Run targeted planner verification commands from `specs/003-story-planner-agent/quickstart.md`
- [X] T025 [P] Run `python3 -m compileall src tests` and record any environment limitations in implementation notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - no dependency on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - benefits from shared subject/intent helpers but remains independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - validates compatibility with US1/US2 planner behavior

### Within Each User Story

- Tests for changed core logic MUST be written and FAIL before implementation
- Shared planner scaffolding before intent-specific scene generation
- Planner implementation before downstream compatibility adjustments
- Story complete before moving to the next priority if delivering incrementally

### Parallel Opportunities

- T004 and T005 can run in parallel after T003
- T007 and T008 can run in parallel
- T012 and T013 can run in parallel
- T017, T018, and T019 can run in parallel
- T023 and T025 can run in parallel during polish

---

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 tests together:
Task: "Add regression test for 记录同一只流浪橘猫在四季中的变化，特征保持一致 in tests/unit/test_story_planner.py"
Task: "Add unit test for journey or growth progression planning in tests/unit/test_story_planner.py"

# Launch all User Story 3 compatibility updates together:
Task: "Update prompt-building assertions for planner-produced concrete scenes in tests/unit/test_prompt_builder.py"
Task: "Update mock pipeline verification for planner compatibility in tests/integration/test_mock_pipeline.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the school-day regression test and confirm four concrete scenes
5. Demo planner-quality improvement before expanding intent coverage

### Incremental Delivery

1. Complete Setup + Foundational → planner boundary and subject/intent core ready
2. Add User Story 1 → test independently → strongest immediate user-facing improvement
3. Add User Story 2 → test independently → broaden intent coverage
4. Add User Story 3 → test independently → confirm no pipeline regressions
5. Finish with polish verification commands

### Parallel Team Strategy

With multiple developers:

1. One developer completes Foundational planner scaffolding
2. After Foundational is done:
   - Developer A: User Story 1 school-day and fallback scenes
   - Developer B: User Story 2 seasonal and journey planning
   - Developer C: User Story 3 compatibility tests and wrapper validation

---

## Notes

- [P] tasks = different files, no dependencies
- [US1], [US2], [US3] labels map tasks directly to prioritized user stories
- Each user story remains independently testable
- Avoid changing provider, CLI, or final layout code unless compatibility work explicitly requires it
