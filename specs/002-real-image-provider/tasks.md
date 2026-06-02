# Tasks: Real image provider integration

**Input**: Design documents from `/specs/002-real-image-provider/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include test tasks whenever the feature changes core logic. External
provider interactions MUST be covered with mocked tests rather than live API
calls unless the spec explicitly requires a real-provider verification step.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/`, `README.md` at repository root
- Paths shown below assume the structure defined in `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the project for real-provider support without changing the core pipeline shape.

- [X] T001 Review and align dependency declarations for one real provider SDK in `pyproject.toml`
- [X] T002 Create the real-provider module scaffold in `src/comic_agent/providers/real_provider.py`
- [X] T003 [P] Create provider selection test file in `tests/unit/test_provider_selection.py`
- [X] T004 [P] Create provider configuration test file in `tests/unit/test_provider_config.py`
- [X] T005 [P] Add a README placeholder section for real-provider setup and testing boundary in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared provider contracts, metadata extensions, and CLI plumbing that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Define provider configuration and run-record models in `src/comic_agent/models/metadata.py`
- [X] T007 [P] Extend request/provider selection inputs in `src/comic_agent/models/comic_request.py`
- [X] T008 [P] Extend the provider interface for configuration validation and generation behavior in `src/comic_agent/providers/base.py`
- [X] T009 [P] Add provider mode and per-panel execution trace fields in `src/comic_agent/models/panel.py`
- [X] T010 Implement provider selection and initialization helpers in `src/comic_agent/cli/generate.py`
- [X] T011 Implement metadata export support for provider mode, retry outcomes, and failure details in `src/comic_agent/pipeline/exporter.py`
- [X] T012 Implement README synchronization checkpoints for provider setup, environment variables, provider selection, and testing boundary in `README.md`

**Checkpoint**: Shared provider foundation is ready and user stories can be implemented independently

---

## Phase 3: User Story 1 - Generate with a real provider (Priority: P1) 🎯 MVP

**Goal**: Let a CLI user generate four real panel images through one configured text-to-image provider while preserving the existing story, prompt, layout, and artifact pipeline.

**Independent Test**: Run `comic-agent generate` with valid provider credentials and real provider selection, then verify four non-placeholder panel images, `comic.png`, and `metadata.json` are created and README documents real-provider usage.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add provider selection and successful real-provider execution tests in `tests/unit/test_provider_selection.py`
- [X] T014 [P] [US1] Add mocked real-provider generation tests for four-panel output in `tests/integration/test_mock_pipeline.py`
- [X] T015 [P] [US1] Add metadata assertions for provider name and provider mode in `tests/unit/test_metadata_export.py`

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement the real text-to-image provider behind the existing interface in `src/comic_agent/providers/real_provider.py`
- [X] T017 [US1] Wire provider selection into CLI request parsing and generation flow in `src/comic_agent/cli/generate.py`
- [X] T018 [US1] Keep the existing story, prompt, and layout pipeline intact while routing panel generation through the selected provider in `src/comic_agent/cli/generate.py`
- [X] T019 [US1] Persist run-level provider name and provider mode in `src/comic_agent/models/metadata.py` and `src/comic_agent/pipeline/exporter.py`
- [X] T020 [US1] Update user-facing setup, provider selection, and real-provider run examples in `README.md`

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Fail clearly when configuration is missing (Priority: P2)

**Goal**: Fail fast and clearly when real-provider configuration or provider output is invalid, while preserving retry limits and metadata traceability.

**Independent Test**: Run the CLI with real provider selection but missing credentials, and verify that the command exits before generation with a clear configuration error and that provider failures are traceable when metadata is written.

### Tests for User Story 2 ⚠️

- [X] T021 [P] [US2] Add environment validation and missing-credential tests in `tests/unit/test_provider_config.py`
- [X] T022 [P] [US2] Add retry and unusable-image failure tests in `tests/unit/test_provider_selection.py`
- [X] T023 [P] [US2] Extend metadata failure-path assertions in `tests/unit/test_metadata_export.py`

### Implementation for User Story 2

- [X] T024 [P] [US2] Implement environment-variable configuration validation for the real provider in `src/comic_agent/providers/real_provider.py`
- [X] T025 [US2] Surface clear configuration and provider failure errors in `src/comic_agent/cli/generate.py`
- [X] T026 [US2] Preserve retry handling and stop safely on unusable provider output in `src/comic_agent/cli/generate.py`
- [X] T027 [US2] Record retry counts, panel failure details, and run failure details in `src/comic_agent/models/metadata.py`, `src/comic_agent/models/panel.py`, and `src/comic_agent/pipeline/exporter.py`
- [X] T028 [US2] Update README configuration, failure behavior, and environment-variable guidance in `README.md`

**Checkpoint**: User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Preserve mock-first testing and MVP scope (Priority: P3)

**Goal**: Keep MockImageProvider as the default automated-test path and document the testing and scope boundary clearly for contributors.

**Independent Test**: Run the existing automated tests without real-provider credentials and verify they continue to pass using the mock provider, then confirm README explains the mock-first testing boundary and deferred image-to-image scope.

### Tests for User Story 3 ⚠️

- [X] T029 [P] [US3] Add tests that confirm mock remains the default automated-test path in `tests/unit/test_provider_selection.py`
- [X] T030 [P] [US3] Extend integration coverage to ensure mock runs still succeed without credentials in `tests/integration/test_mock_pipeline.py`
- [X] T031 [P] [US3] Add assertions that reference-image input remains outside real image-to-image behavior in `tests/unit/test_provider_config.py`

### Implementation for User Story 3

- [X] T032 [P] [US3] Ensure mock remains the default provider for automated-test-safe flows in `src/comic_agent/cli/generate.py`
- [X] T033 [US3] Preserve current reference-image metadata-only handling for real-provider runs in `src/comic_agent/cli/generate.py` and `src/comic_agent/providers/real_provider.py`
- [X] T034 [US3] Update README testing boundary, mock-first guidance, and deferred image-to-image scope in `README.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final alignment, cleanup, and smallest relevant verification

- [X] T035 [P] Align `specs/002-real-image-provider/quickstart.md` with final provider selection, setup, and verification commands
- [X] T036 [P] Review `README.md` against `specs/002-real-image-provider/contracts/cli-contract.md`
- [X] T037 Run the smallest relevant real verification command for this feature, such as `pytest tests/unit/test_provider_selection.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) and delivers the real-provider MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2), but builds on the provider path introduced in US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) and verifies test-boundary preservation across US1/US2 behavior

### Within Each User Story

- Tests for changed core logic MUST be written and fail before implementation
- Shared models and provider interfaces come before CLI integration
- Provider configuration validation comes before real generation calls
- Metadata and README updates must land in the same story phase as the user-facing behavior change
- Story completion should be verified before moving to the next priority when shipping incrementally

### Parallel Opportunities

- `T003`, `T004`, and `T005` can run in parallel during Setup
- `T007`, `T008`, and `T009` can run in parallel during Foundational work
- `T013`, `T014`, and `T015` can run in parallel for US1
- `T021`, `T022`, and `T023` can run in parallel for US2
- `T029`, `T030`, and `T031` can run in parallel for US3
- `T035` and `T036` can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
Task: "Add provider selection and successful real-provider execution tests in tests/unit/test_provider_selection.py"
Task: "Add mocked real-provider generation tests for four-panel output in tests/integration/test_mock_pipeline.py"
Task: "Add metadata assertions for provider name and provider mode in tests/unit/test_metadata_export.py"

# Launch independent implementation tasks after provider contract work is done:
Task: "Implement the real text-to-image provider behind the existing interface in src/comic_agent/providers/real_provider.py"
Task: "Update user-facing setup, provider selection, and real-provider run examples in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify real-provider selection and output package behavior
5. Review README coverage for setup and usage

### Incremental Delivery

1. Complete Setup + Foundational → provider-ready foundation
2. Add User Story 1 → test independently → demo real generation flow
3. Add User Story 2 → test independently → validate configuration and failure handling
4. Add User Story 3 → test independently → lock down mock-first test boundary
5. Finish with the smallest relevant verification command

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 real-provider execution path
   - Developer B: User Story 2 configuration validation and failure metadata
   - Developer C: User Story 3 mock-first testing boundary and documentation updates
3. Merge only after each story passes its own tests and documentation checks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps tasks to user stories for traceability
- Each user story is independently completable and testable
- Real provider calls in automated tests remain mocked or stubbed
- README updates are required whenever provider behavior, setup, or test commands change
