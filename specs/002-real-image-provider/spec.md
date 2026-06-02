# Feature Specification: Real image provider integration

**Feature Branch**: `[002-real-image-provider]`  
**Created**: 2026-05-28  
**Status**: Draft  
**Input**: User description: "Add a real image provider integration for the four-panel comic agent. Implement OpenAIImageProvider or another real provider behind the existing provider interface. Keep MockImageProvider as the default for tests. Read API keys from environment variables. Support text-to-image first. Defer real image-to-image unless explicitly included."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate with a real provider (Priority: P1)

As a user running the comic agent from the CLI, I want to generate the four
panel images through a configured real image provider so that the output comic
contains actual generated artwork instead of placeholder mock panels.

**Why this priority**: This is the core value of the feature. Without a real
provider, the comic pipeline remains only a mock demonstration.

**Independent Test**: Configure valid provider credentials in the environment,
run the CLI with a theme and provider selection, and verify that the run
produces four non-placeholder panel images, a final comic image, and
`metadata.json`.

**Acceptance Scenarios**:

1. **Given** valid provider credentials are available, **When** the user runs
   the CLI with a theme and selects the real provider, **Then** the system
   generates exactly four panel images through that provider and exports the
   final comic package successfully.
2. **Given** the user does not explicitly select the mock provider, **When**
   the real provider is enabled and credentials are present, **Then** the
   system uses the configured real provider for panel generation and records the
   provider name in metadata.

---

### User Story 2 - Fail clearly when configuration is missing (Priority: P2)

As a user or contributor, I want clear errors when provider credentials or
required provider configuration are missing so that I can correct the setup
without guessing why generation failed.

**Why this priority**: Real provider support is only usable if setup failures
are understandable and safe.

**Independent Test**: Run the CLI with the real provider selected but with the
required environment variables missing, and verify that the command exits
without partial generation and shows a clear configuration error.

**Acceptance Scenarios**:

1. **Given** the real provider is selected and credentials are missing,
   **When** the user runs the CLI, **Then** the command fails with a clear
   setup error describing the missing environment requirement.
2. **Given** the real provider returns an upstream generation failure,
   **When** the system retries within the allowed limit, **Then** the final
   failure is reported clearly and metadata reflects the retry outcome if a
   metadata record is produced.

---

### User Story 3 - Preserve mock-first testing and MVP scope (Priority: P3)

As a contributor, I want the existing mock provider and tests to remain the
default verification path so that automated tests do not depend on live
credentials, network access, or paid provider usage.

**Why this priority**: The project constitution requires verifiable,
mock-friendly testing and no unnecessary external coupling.

**Independent Test**: Run the existing unit and integration tests without real
provider credentials and verify that they still pass using the mock provider.

**Acceptance Scenarios**:

1. **Given** a local or CI test environment without provider credentials,
   **When** the test suite runs, **Then** the tests continue to use the mock
   provider and do not require live provider access.
2. **Given** contributor documentation is updated, **When** a contributor reads
   the README, **Then** they can understand the difference between mock and real
   provider usage, required environment variables, and current scope limits.

### Edge Cases

- What happens when the user selects the real provider but one or more required
  environment variables are unset or empty?
- What happens when the upstream provider accepts some panel requests but a
  later panel generation attempt fails permanently?
- How does the system behave when the provider returns content that is empty,
  unreadable, or not a supported image format?
- What happens when the user provides both a real provider selection and a
  reference image, even though real image-to-image is still out of scope?
- How does the system distinguish between test runs that must stay mock-only and
  manual runs that are allowed to call the real provider?
- What happens when a theme implies multi-stage progression, such as four
  seasons, but each provider call must still generate exactly one single-scene
  full-frame image?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support selection between the existing mock image
  provider and one real image provider for panel generation.
- **FR-002**: The system MUST allow users to run the four-panel comic pipeline
  with the real provider through the existing CLI workflow.
- **FR-003**: The system MUST read any required real-provider credentials from
  environment variables rather than from CLI arguments or source-controlled
  files.
- **FR-004**: The system MUST validate real-provider configuration before the
  first external generation request is sent.
- **FR-005**: The system MUST support real text-to-image generation for each of
  the four panel prompts.
- **FR-005a**: The system MUST ensure each provider call receives a prompt for
  exactly one full-frame single-scene panel image rather than an internal
  collage, split-screen, grid, montage, comparison sheet, or embedded comic
  layout.
- **FR-006**: The system MUST preserve the current four-panel story structure,
  prompt generation rules, metadata export, and final 2x2 composition flow when
  a real provider is used.
- **FR-007**: The system MUST continue to support the mock provider as the
  explicit provider used by automated tests and credential-free verification.
- **FR-008**: The system MUST provide clear user-facing errors when real-provider
  credentials are missing, invalid, or rejected.
- **FR-009**: The system MUST record the provider used for a run in
  `metadata.json`.
- **FR-010**: The system MUST record whether panel generation used mock or real
  provider behavior in a way that contributors can verify from outputs or
  metadata.
- **FR-011**: The system MUST retain the current retry limit for panel image
  generation when the real provider is used.
- **FR-012**: The system MUST reject or stop a real-provider run safely if the
  provider returns unusable image output for a panel.
- **FR-013**: The system MUST document the setup steps, required environment
  variables, provider-selection workflow, and testing boundary in `README.md`.
- **FR-014**: The system MUST keep reference-image handling within the current
  MVP boundary unless a later feature explicitly adds real image-to-image
  support.
- **FR-015**: The system MUST define explicit output artifacts, including the
  four generated panel images, final comic image, and `metadata.json`, for both
  mock and real-provider runs.
- **FR-016**: The system MUST specify that external provider interactions are
  part of this feature for manual runs, while automated tests continue to use
  mock substitution.
- **FR-017**: The system MUST preserve existing character-consistency,
  style-consistency, and safety constraints before invoking the real provider.
- **FR-018**: The system MUST append strong single-image constraints to every
  final panel-generation prompt, including: single full-frame illustration, one
  scene only, no collage, no split-screen, no grid, no internal comic layout,
  no four-panel layout inside the image, no montage, no seasonal comparison
  layout, no text labels, no captions, and no speech bubbles.
- **FR-019**: The system MUST derive `character_bible` content from concrete
  visual identity cues for the subject and MUST NOT simply copy the full theme
  text as the character summary.
- **FR-020**: The system MUST keep `style_bible` and final panel prompts free
  of page-level layout instructions that belong only to the downstream 2x2
  composition stage.
- **FR-021**: For four-season or similar time-progression themes, the story
  planner MUST assign one stage of progression to each of the four panels so
  each provider call remains a single-scene prompt.

### Key Entities *(include if feature involves data)*

- **Provider Configuration**: The user-selectable provider mode and required
  environment-based credentials needed to authorize a real generation run.
- **Provider Run Record**: The run-level information describing which provider
  handled generation, whether generation succeeded, and any retry or failure
  outcomes that should be reflected in metadata.
- **Panel Generation Result**: The output of a single panel generation attempt,
  including a usable image artifact or a failure state that can trigger retry or
  stop the run.
- **Single-Scene Panel Prompt**: The final provider-facing prompt for one panel,
  combining story context, character and style guidance, and explicit
  anti-collage constraints while excluding page-level layout instructions.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: The system must continue applying unsafe-theme rejection and
  unsafe-prompt rewrite rules before any external provider call. Missing or
  invalid credentials must fail fast before image generation begins.
- **Prompt Boundary Rules**: Page-level comic layout instructions belong only to
  the final compositor. Provider-facing panel prompts must describe one image,
  one moment, and one scene.
- **Out of Scope**: Real image-to-image generation, per-panel reference images,
  provider-specific tuning controls beyond minimal setup needed to run, web UI,
  queueing, background execution, and replacing the mock provider in automated
  tests.
- **Verification Plan**: After implementation, run the smallest relevant real
  verification command: a targeted provider integration test with mocking plus
  one manual CLI smoke run using the mock provider. If a configured real
  provider is available locally, an additional manual CLI run with the real
  provider should be performed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user with valid real-provider credentials can complete one
  four-panel generation run and receive all expected output files in a single
  CLI invocation.
- **SC-002**: A user without required credentials receives a clear actionable
  setup error before any panel generation attempt begins.
- **SC-003**: Contributors can run the automated test suite without live
  credentials, network access, or paid provider usage.
- **SC-004**: For successful real-provider runs, the generated output package
  identifies which provider produced the panels and preserves the same output
  contract as mock runs.
- **SC-005**: For themes involving seasonal or temporal progression, each saved
  `final_image_prompt` describes only one stage or moment and does not contain
  page-level layout instructions.

## Assumptions

- At least one real provider can generate a single panel image directly from a
  text prompt without requiring additional workflow state.
- Provider credentials are available through environment variables in developer
  or user shells.
- The existing provider interface and CLI can be extended without replacing the
  four-panel story pipeline or output contract.
- Manual real-provider verification may depend on local credentials and network
  access, but automated tests must not.
- Reference-image input remains metadata-only for this feature unless a later
  specification expands scope to real image-to-image behavior.
- The prompt pipeline can enforce provider-safe single-scene constraints without
  modifying the real-provider transport layer itself.
