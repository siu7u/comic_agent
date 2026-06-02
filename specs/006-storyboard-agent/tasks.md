# Tasks: StoryboardAgent for four-panel story expansion

**Input**: Design documents from `/specs/006-storyboard-agent/`
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

**Purpose**: Capture the storyboard-agent scope and prepare feature-specific verification files.

- [x] T001 Create storyboard planner test module scaffold in `tests/unit/test_story_planner.py`
- [x] T002 Review storyboard expansion requirements, contract, and verification scenarios in `specs/006-storyboard-agent/spec.md`, `specs/006-storyboard-agent/contracts/storyboard-expansion-contract.md`, and `specs/006-storyboard-agent/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared subject resolution, story-type detection, and compatibility boundaries required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Define StoryboardAgent boundaries, compatibility wrapper behavior, and story type priority in `src/comic_agent/pipeline/story_planner.py` and `specs/006-storyboard-agent/contracts/storyboard-expansion-contract.md`
- [x] T004 [P] Add foundational subject extraction coverage in `tests/unit/test_story_planner.py`
- [x] T005 [P] Add foundational story type detection coverage in `tests/unit/test_story_planner.py`
- [x] T006 [P] Add foundational compatibility coverage for `build_story_structure(request)` in `tests/unit/test_story_planner.py`
- [x] T007 Implement shared subject resolution and story type selection scaffolding in `src/comic_agent/pipeline/story_planner.py`
- [x] T008 Implement the internal StoryboardAgent entrypoint and compatibility delegation in `src/comic_agent/pipeline/story_planner.py`
- [x] T009 Preserve story-structure shape and downstream pipeline expectations in `src/comic_agent/models/panel.py`, `src/comic_agent/models/metadata.py`, and `src/comic_agent/cli/generate.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Expand Simple Daily Stories (Priority: P1) 🎯 MVP

**Goal**: Expand simple day-in-the-life prompts into four concrete, distinct storyboard panels.

**Independent Test**: Submit `一只小兔子上学的一天` and verify the planner returns exactly four concrete scenes with captions `Morning`, `On the Way`, `At School`, and `Going Home`.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Add regression coverage for `一只小兔子上学的一天` in `tests/unit/test_story_planner.py`
- [x] T011 [P] [US1] Add prompt-builder compatibility assertions for concrete school-day scenes in `tests/unit/test_prompt_builder.py`

### Implementation for User Story 1

- [x] T012 [US1] Implement day-in-the-life storyboard pattern captions, actions, emotions, and framing in `src/comic_agent/pipeline/story_planner.py`
- [x] T013 [US1] Implement concrete school-day scene expansion for home departure, travel, school activity, and return home in `src/comic_agent/pipeline/story_planner.py`
- [x] T014 [US1] Ensure day-in-the-life panel descriptions avoid repeated theme text and page-level layout instructions in `src/comic_agent/pipeline/story_planner.py`
- [x] T015 [US1] Verify subject propagation from storyboard output into prompt generation for school-day stories in `src/comic_agent/pipeline/prompt_builder.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Expand Recognized Story Structures (Priority: P2)

**Goal**: Expand seasonal, journey, and problem-solving prompts into stage-appropriate four-panel storyboard sequences.

**Independent Test**: Submit `记录同一只流浪橘猫在四季中的变化，特征保持一致`, `一只狐狸放飞灯笼`, and `机器人修好城市的灯` and verify each receives the correct structure with four concrete scene beats.

### Tests for User Story 2 ⚠️

- [x] T016 [P] [US2] Add seasonal progression regression coverage for `记录同一只流浪橘猫在四季中的变化，特征保持一致` in `tests/unit/test_story_planner.py`
- [x] T017 [P] [US2] Add journey or adventure regression coverage for `一只狐狸放飞灯笼` in `tests/unit/test_story_planner.py`
- [x] T018 [P] [US2] Add problem-solving coverage for `机器人修好城市的灯` in `tests/unit/test_story_planner.py`

### Implementation for User Story 2

- [x] T019 [US2] Implement seasonal progression storyboard expansion with one season per panel in `src/comic_agent/pipeline/story_planner.py`
- [x] T020 [US2] Implement journey or adventure storyboard expansion with departure, encounter, turning point, and resolution beats in `src/comic_agent/pipeline/story_planner.py`
- [x] T021 [US2] Implement problem-solving storyboard expansion with problem, search, solution, and payoff beats in `src/comic_agent/pipeline/story_planner.py`
- [x] T022 [US2] Enforce concrete scene descriptions, panel-level actions, and stage-specific emotions across recognized structures in `src/comic_agent/pipeline/story_planner.py`
- [x] T023 [US2] Ensure recognized structures remain image-friendly and avoid multi-scene or page-layout wording in `src/comic_agent/pipeline/story_planner.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Preserve Stable Pipeline Contracts (Priority: P3)

**Goal**: Keep CLI behavior, prompt generation, provider behavior, layout, and metadata compatibility stable while introducing StoryboardAgent.

**Independent Test**: Use `build_story_structure(request)` and the mock-provider pipeline to confirm downstream prompt generation and final comic assembly still work without network access.

### Tests for User Story 3 ⚠️

- [x] T024 [P] [US3] Update compatibility assertions for `build_story_structure(request)` and fallback story expansion in `tests/unit/test_story_planner.py`
- [x] T025 [P] [US3] Update prompt-builder compatibility coverage for storyboard-expanded scenes in `tests/unit/test_prompt_builder.py`
- [x] T026 [P] [US3] Update mock pipeline coverage to confirm storyboard-expanded stories remain compatible in `tests/integration/test_mock_pipeline.py`

### Implementation for User Story 3

- [x] T027 [US3] Preserve compatibility wrapper behavior and downstream story contract in `src/comic_agent/pipeline/story_planner.py`
- [x] T028 [US3] Keep provider interfaces and final composition behavior unchanged while storyboard expansion remains upstream in `src/comic_agent/providers/base.py`, `src/comic_agent/providers/mock.py`, and `src/comic_agent/providers/real_provider.py`
- [x] T029 [US3] Keep metadata and CLI generation flow compatible with storyboard-expanded output in `src/comic_agent/cli/generate.py` and `src/comic_agent/models/metadata.py`
- [x] T030 [US3] Update contributor and user workflow documentation for StoryboardAgent architecture only if required in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cross-story cleanup

- [x] T031 [P] Review storyboard scene quality and scope coverage against `specs/006-storyboard-agent/contracts/storyboard-expansion-contract.md`
- [ ] T032 Run targeted mock-safe verification commands from `specs/006-storyboard-agent/quickstart.md`
- [x] T033 [P] Run `python3 -m compileall src tests` and document any environment limitations in implementation notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - establishes the baseline StoryboardAgent expansion quality for common daily-life prompts
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - builds additional recognized structures on top of shared subject and story-type scaffolding
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - validates compatibility once storyboard expansion behavior exists

### Within Each User Story

- Tests for changed core logic MUST be written and FAIL before implementation
- Subject and structure rules before concrete panel-beat expansion
- Storyboard expansion before downstream compatibility updates
- Story complete before moving to next priority

### Parallel Opportunities

- T004, T005, and T006 can run in parallel after T003
- T010 and T011 can run in parallel
- T016, T017, and T018 can run in parallel
- T024, T025, and T026 can run in parallel
- T031 and T033 can run in parallel during polish

---

## Parallel Example: User Story 2

```bash
# Launch all recognized-structure tests for User Story 2 together:
Task: "Add seasonal progression regression coverage for 记录同一只流浪橘猫在四季中的变化，特征保持一致 in tests/unit/test_story_planner.py"
Task: "Add journey or adventure regression coverage for 一只狐狸放飞灯笼 in tests/unit/test_story_planner.py"
Task: "Add problem-solving coverage for 机器人修好城市的灯 in tests/unit/test_story_planner.py"

# Launch all User Story 3 compatibility tests together:
Task: "Update compatibility assertions for build_story_structure(request) and fallback story expansion in tests/unit/test_story_planner.py"
Task: "Update prompt-builder compatibility coverage for storyboard-expanded scenes in tests/unit/test_prompt_builder.py"
Task: "Update mock pipeline coverage to confirm storyboard-expanded stories remain compatible in tests/integration/test_mock_pipeline.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm `一只小兔子上学的一天` expands into four concrete school-day panels
5. Demo the baseline StoryboardAgent before adding more structures

### Incremental Delivery

1. Complete Setup + Foundational → StoryboardAgent boundary and compatibility wrapper ready
2. Add User Story 1 → test independently → deploy/demo as the first concrete storyboard improvement
3. Add User Story 2 → test independently → expand the supported structure set
4. Add User Story 3 → test independently → confirm pipeline stability
5. Finish with polish verification commands

### Parallel Team Strategy

With multiple developers:

1. One developer completes Foundational planner scaffolding and compatibility delegation
2. After Foundational is done:
   - Developer A: User Story 1 day-in-the-life expansion
   - Developer B: User Story 2 recognized structure expansions
   - Developer C: User Story 3 compatibility tests and documentation

---

## Notes

- [P] tasks = different files, no dependencies
- [US1], [US2], [US3] labels map tasks directly to prioritized user stories
- Each user story remains independently testable
- Automated verification must remain mock-safe and must not require live provider access
- Avoid changing provider responsibilities or final layout behavior while implementing storyboard expansion
