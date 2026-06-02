# Feature Specification: LM-assisted story planner

**Feature Branch**: `[004-lm-story-planner]`  
**Created**: 2026-05-29  
**Status**: Draft  
**Input**: User description: "Create a new English spec for an opt-in lightweight LM integration for story planning."

## Clarifications

### Session 2026-05-29

- Q: How should users explicitly opt into LM-assisted planning? → A: Add an explicit CLI flag for planner selection on each run.
- Q: What output format should the LM-assisted planner return? → A: One strict JSON object containing the planning result.
- Q: What planning traceability should metadata record? → A: Record both the requested planner mode and the actual planner used after fallback.
- Q: How should LM configuration be provided? → A: Read LM configuration from environment variables.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Opt Into LM-Assisted Planning (Priority: P1)

As a user generating comics from the CLI, I want an explicit way to opt into
LM-assisted story planning so that I can compare stronger storyboard planning
against the current rule-based planner.

**Why this priority**: The core value of this feature is controlled evaluation
of LM-assisted planning quality while preserving the current stable default
planner.

**Independent Test**: Run comic generation with the planner-selection CLI flag
set to LM-assisted planning and verify that the system attempts LM-assisted
planning, validates the result, and still returns a valid four-panel story
structure.

**Acceptance Scenarios**:

1. **Given** a user explicitly enables LM-assisted story planning, **When** the
   planner is invoked, **Then** the system uses the LM-assisted planning path
   before any fallback logic.
2. **Given** a user does not explicitly enable LM-assisted story planning,
   **When** the planner is invoked, **Then** the system follows the current
   environment-controlled default planner mode.

---

### User Story 2 - Fallback Safely on LM Failure (Priority: P2)

As a contributor or user, I want LM-assisted planning to fail closed and fall
back to the deterministic rule-based planner so that planning quality can be
improved experimentally without breaking the existing comic generation flow.

**Why this priority**: LM-assisted planning is only viable if failure modes are
predictable, bounded, and compatible with current pipeline guarantees.

**Independent Test**: Simulate malformed, incomplete, timed-out, or rejected
LM responses and verify that the system falls back to the existing rule-based
planner while preserving a valid four-panel output contract.

**Acceptance Scenarios**:

1. **Given** LM-assisted planning is enabled, **When** the LM response is
   invalid, incomplete, or schema-noncompliant, **Then** the system falls back
   to the rule-based planner automatically.
2. **Given** LM-assisted planning is enabled, **When** the LM planner is
   unavailable or times out, **Then** the system still completes planning
   through the rule-based planner without requiring user intervention.

---

### User Story 3 - Keep Tests and Pipeline Behavior Stable (Priority: P3)

As a contributor, I want LM-assisted planning to be testable through mocked or
stubbed planner responses so that automated tests remain deterministic and do
not require live model access, network access, or changes to provider and layout
behavior.

**Why this priority**: The existing pipeline already depends on mock-safe
testing and stable downstream contracts. LM-assisted planning must integrate
without weakening those guarantees.

**Independent Test**: Run planner and pipeline tests using mocked LM responses
and verify that story planning, prompt generation, metadata export, provider
behavior, and final image composition remain compatible.

**Acceptance Scenarios**:

1. **Given** automated tests run without live model credentials, **When**
   LM-assisted planning behavior is tested, **Then** all coverage uses mocks or
   stubs instead of real model calls.
2. **Given** LM-assisted planning returns a valid structured plan, **When** the
   rest of the pipeline executes, **Then** prompt generation, provider calls,
   metadata export, and final layout behavior remain unchanged in contract.

### Edge Cases

- What happens when LM-assisted planning returns fewer than four panel beats?
- What happens when LM-assisted planning returns four panels but one or more
  required fields are missing or empty?
- What happens when the LM returns page-level layout instructions, collage
  requests, or a full comic page description instead of one scene per panel?
- What happens when LM-assisted planning returns a subject that conflicts with
  an explicitly provided `--character` value?
- What happens when both the LM result and the fallback rule-based result are
  available for the same request and differ substantially in intent?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support an explicit opt-in path for LM-assisted
  story planning and MUST keep the existing rule-based planner as the default
  planning behavior.
- **FR-001a**: The explicit opt-in path for LM-assisted story planning MUST be
  a CLI flag provided on a per-run basis.
- **FR-002**: The system MUST expose one internal LM-assisted planning
  component for story planning without introducing an external agent framework.
- **FR-002a**: LM configuration for this feature MUST be read from environment
  variables rather than from planner-selection CLI arguments.
- **FR-003**: The LM-assisted planning path MUST remain limited to a lightweight
  planning step and MUST NOT introduce multi-step autonomous agent loops.
- **FR-004**: The LM-assisted planner MUST produce or request one structured
  four-panel storyboard result that can be validated before conversion into the
  existing story structure contract.
- **FR-004a**: The LM-assisted planner MUST return one strict JSON object as
  its planning result payload.
- **FR-005**: The system MUST validate LM-assisted planning output before using
  it downstream.
- **FR-006**: The system MUST reject or ignore LM-assisted planning output that
  does not produce exactly four panels.
- **FR-007**: The system MUST reject or ignore LM-assisted planning output that
  omits required panel fields such as caption, scene description, visual
  description, action, emotion, camera framing, or dialogue.
- **FR-008**: The system MUST reject or ignore LM-assisted planning output that
  includes page-level layout instructions, collage directions, split-screen
  requests, or full comic page descriptions.
- **FR-009**: The system MUST automatically fall back to the deterministic
  rule-based planner when LM-assisted planning fails, times out, is unavailable,
  or produces invalid output.
- **FR-010**: The fallback path MUST preserve the existing four-panel
  `StoryStructure` output contract.
- **FR-011**: When `request.character` is explicitly provided, the system MUST
  preserve that character as the authoritative subject even if the LM suggests a
  different subject.
- **FR-012**: The LM-assisted planner MUST preserve the current single-scene
  panel requirement and MUST NOT instruct any panel to contain multiple panels
  or an internal comic layout.
- **FR-013**: The LM-assisted planner MUST preserve compatibility with the
  current prompt-generation, provider, metadata, and final layout pipeline.
- **FR-014**: The feature MUST preserve existing provider behavior, including
  mock and Wanx image generation behavior.
- **FR-015**: The feature MUST preserve the final composed comic contract,
  including the current `1054x1054` image size and `10px` `田`-shaped grid
  border.
- **FR-016**: Automated tests for this feature MUST use mocked or stubbed
  LM-assisted planning behavior and MUST NOT require live model access or
  network access.
- **FR-017**: The system MUST record enough planning traceability in metadata or
  logs for contributors to determine whether a run used LM-assisted planning or
  the fallback rule-based planner.
- **FR-017a**: Metadata traceability for this feature MUST record both the
  requested planner mode and the actual planner used after any fallback.
- **FR-018**: The system MUST define explicit output artifacts, including the
  continued use of `metadata.json`, generated prompts, and final image files.
- **FR-019**: The system MUST specify whether external LM interactions are part
  of this feature and how they are substituted in automated tests.
- **FR-019a**: Any required LM credentials or endpoint configuration for manual
  runs MUST be supplied through environment variables.
- **FR-020**: The system MUST preserve current safety constraints before image
  generation and MUST ensure LM-assisted planning does not bypass existing
  unsafe-theme rejection behavior.
- **FR-021**: README.md MUST be updated if contributor or user workflow changes
  because of planner-selection behavior, setup requirements, or testing
  expectations.

### Key Entities *(include if feature involves data)*

- **LM-Assisted Planner**: The internal lightweight planning component that
  requests one structured story-planning result from an LM and converts a valid
  response into the existing story structure contract.
- **Planner Selection Mode**: The user- or system-visible planning mode that
  determines whether planning uses the default rule-based planner or the
  explicit opt-in LM-assisted planner.
- **LM Configuration**: The environment-based runtime settings required to
  authorize or target the LM-assisted planning call for manual runs.
- **Validated Planning Result**: The structured planning payload accepted from
  the LM as one strict JSON object after schema and content validation and
  before downstream prompt
  generation.
- **Fallback Planning Outcome**: The rule-based story structure used when
  LM-assisted planning is disabled or invalid.
- **Planner Execution Record**: The run-level trace indicating which planner was
  requested and which planner actually produced the story structure.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: Unsafe themes must continue to be rejected before image
  generation. LM-assisted planning must not introduce page-level layout
  instructions, multi-panel image requests, or content that bypasses existing
  single-scene prompt safety constraints.
- **Out of Scope**: Changing final layout behavior, modifying image providers,
  real image-to-image generation, per-panel reference images, introducing
  external agent orchestration frameworks, multi-step autonomous agents, web UI,
  database, queueing, background jobs, or replacing the rule-based planner as
  the mandatory default behavior in this feature.
- **Verification Plan**: After implementation, run mocked planner unit tests,
  planner fallback tests, and one mock-safe pipeline compatibility command.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can explicitly enable LM-assisted planning for a run using
  a CLI flag while leaving the default rule-based planning behavior unchanged
  for ordinary runs.
- **SC-002**: When LM-assisted planning fails or returns invalid output, the
  system still completes planning through the fallback rule-based planner and
  preserves a valid four-panel output contract.
- **SC-003**: Automated tests cover valid LM-assisted planning, invalid LM
  output, and fallback behavior without requiring live model access or network
  access.
- **SC-004**: Downstream prompt generation, provider execution, metadata export,
  and final comic composition continue to work without contract changes for
  successful LM-assisted or fallback planning runs.
- **SC-005**: Contributors can determine from metadata whether a run requested
  LM-assisted planning and whether the final story came from the LM-assisted or
  fallback rule-based planner.
- **SC-006**: Users can enable LM-assisted planning with a CLI flag without
  needing to place LM credentials or connection details in CLI arguments.

## Assumptions

- The current rule-based `StoryPlannerAgent` remains available and stable as the
  fallback planner.
- A lightweight LM integration can be isolated to one planning request and one
  validated structured response.
- A single strict JSON object is sufficient to represent the planning result
  needed by downstream validation and conversion.
- The team prefers controlled experimentation over replacing the default
  planning path immediately.
- Mocked or stubbed LM responses are sufficient to verify the feature during
  automated testing.
- The CLI can accept one additional planner-selection flag without disrupting
  existing comic-generation workflows.
- Environment-variable-based configuration is acceptable for manual LM-assisted
  planning runs and aligns with existing project configuration patterns.
