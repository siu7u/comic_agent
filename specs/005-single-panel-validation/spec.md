# Feature Specification: Single-panel generation validation and retry

**Feature Branch**: `[005-single-panel-validation]`  
**Created**: 2026-05-29  
**Status**: Draft  
**Input**: User description: "If we approach the current problem from architecture instead of only from prompt wording, create a spec for solving single-panel generation failures such as nested multi-panel or storyboard-like images."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reject Broken Single-Panel Images (Priority: P1)

As a user generating a four-image comic, I want the system to automatically
detect when one generated image is not a valid single-scene illustration so
that I do not receive a final comic containing a nested comic page or storyboard
inside one panel.

**Why this priority**: The current failure mode is user-visible and directly
undermines the core output contract, even when the generation request itself
completes successfully.

**Independent Test**: Provide one generated panel result that is classified as
invalid for single-panel use and verify that the run does not silently accept it
as a successful panel.

**Acceptance Scenarios**:

1. **Given** a generated image that appears to contain multiple internal frames
   or sub-images, **When** panel validation runs, **Then** the system marks the
   attempt as invalid for single-panel use.
2. **Given** a generated image that represents one clear continuous scene,
   **When** panel validation runs, **Then** the system accepts it as a valid
   panel without requiring a retry.

---

### User Story 2 - Retry with Stronger Generation Strategies (Priority: P2)

As a user, I want the system to retry a failed panel with a stronger
single-scene strategy so that occasional provider drift does not ruin an
otherwise valid comic run.

**Why this priority**: Detection alone is not enough. The system must recover
without forcing the user to manually rerun the entire comic.

**Independent Test**: Simulate one invalid first attempt and verify that the
system requests at least one retry using a stricter strategy before concluding
the panel failed.

**Acceptance Scenarios**:

1. **Given** a panel generation attempt that fails single-panel validation,
   **When** retry policy is applied, **Then** the system makes another attempt
   using a stronger single-scene generation strategy.
2. **Given** a later retry attempt that passes validation, **When** the comic
   run completes, **Then** the accepted panel is used in the final comic and
   metadata records both the failed and successful attempts.

---

### User Story 3 - Preserve Stable Pipeline Contracts (Priority: P3)

As a contributor, I want validation and retry to fit inside the existing comic
pipeline without changing provider selection, final layout, or metadata
traceability expectations so that the architecture improves reliability without
destabilizing the rest of the system.

**Why this priority**: The feature is valuable only if it reduces bad outputs
while keeping the CLI, provider abstraction, and final composition contract
stable.

**Independent Test**: Run mock-safe pipeline verification and confirm that the
comic pipeline still produces four panel records, one final `1054x1054` comic,
and traceable metadata while capturing validation and retry outcomes.

**Acceptance Scenarios**:

1. **Given** a comic run with no validation failures, **When** the feature is
   enabled, **Then** the pipeline still produces the same final layout and
   compatible metadata structure as before, with additional attempt trace data
   only where needed.
2. **Given** a comic run where one panel requires retries, **When** the run
   completes or fails, **Then** metadata shows which attempts were rejected,
   which strategy was ultimately accepted, and whether the panel ever passed
   validation.

### Edge Cases

- What happens when a panel attempt is ambiguous rather than clearly valid or
  clearly invalid for single-panel use?
- What happens when every retry strategy still produces invalid single-panel
  output for one panel?
- What happens when the provider returns an unreadable or partial image that
  cannot even be evaluated by the single-panel validator?
- What happens when the same panel prompt is valid for one provider but often
  invalid for another provider?
- What happens when a generated image is visually a single scene but also
  contains unwanted text labels or comic-style separators?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST introduce an internal single-panel validation step
  between image generation and panel acceptance.
- **FR-002**: The validation step MUST determine whether a generated image is
  acceptable as one full-frame single-scene panel.
- **FR-003**: The validation step MUST be able to reject images that appear to
  contain multiple internal frames, storyboard-like subdivision, split-screen
  layouts, grids, montages, comparison sheets, or other multi-scene
  compositions.
- **FR-004**: The system MUST treat a rejected panel attempt as a failed panel
  generation attempt even if the provider call itself returned image data.
- **FR-005**: The system MUST define at least one stricter retry strategy that
  is used only after validation rejects a panel attempt.
- **FR-006**: Retry strategy progression MUST be deterministic and bounded so
  the system does not loop indefinitely.
- **FR-007**: The system MUST preserve the existing one-panel-at-a-time
  provider call model.
- **FR-008**: The system MUST preserve the current final 2x2 comic layout,
  including the `1054x1054` final image size and `10px` `田`-shaped grid
  border.
- **FR-009**: The system MUST preserve the existing CLI surface unless a small
  additive control is clearly required.
- **FR-010**: The system MUST preserve existing provider selection behavior for
  mock and Wanx generation.
- **FR-011**: The system MUST record panel-attempt validation outcomes in
  metadata, including which attempts were rejected and why.
- **FR-012**: The system MUST record which retry strategy, if any, produced the
  accepted panel.
- **FR-013**: The system MUST record when a panel run ultimately fails because
  no attempt passed single-panel validation.
- **FR-014**: The system MUST allow automated tests to simulate accepted and
  rejected panel attempts without network access or real provider credentials.
- **FR-015**: The system MUST keep prompt generation, story planning, provider
  execution, and validation as separable pipeline responsibilities.
- **FR-016**: The system MUST define explicit validation coverage for accepted
  panels, rejected panels, retry progression, retry exhaustion, and metadata
  traceability.
- **FR-017**: The system MUST specify whether validation is heuristic,
  rule-based, model-assisted, or hybrid, and MUST keep automated verification
  mock-safe regardless of the chosen runtime validator.
- **FR-018**: The system MUST preserve safety behavior so unsafe themes are
  still rejected before provider-side image generation begins.
- **FR-019**: The system MUST define explicit output artifacts, including panel
  images, final comic image, metadata, and any per-attempt validation traces
  retained by the feature.
- **FR-020**: README.md MUST be updated if contributor workflow, runtime
  configuration, or debugging expectations change because validation and retry
  are added.

### Key Entities *(include if feature involves data)*

- **PanelGenerationAttempt**: One provider-backed attempt to generate an image
  for a single panel, including the prompt strategy used and the returned image
  outcome.
- **SinglePanelValidationResult**: The decision record for one panel attempt,
  including whether the image is accepted, rejected, or ambiguous and the
  reason for that decision.
- **RetryStrategyProfile**: A named generation strategy used for the first
  attempt or later retries, with progressively stronger single-scene
  constraints.
- **PanelAttemptTrace**: The metadata-facing record that links attempts,
  validation results, strategy usage, and final acceptance or failure.
- **AcceptedPanelArtifact**: The final panel image selected for composition
  after validation and any retries have completed.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: Unsafe themes remain blocked before provider generation.
  Validation and retry must never bypass existing safety checks, and invalid
  images must be rejected before they are composed into the final comic.
- **Out of Scope**: Changing the final 2x2 layout, adding new image providers,
  adding a web UI, adding a database, introducing background jobs, introducing
  an external agent framework, or requiring live provider access in automated
  tests.
- **Verification Plan**: After implementation, run the smallest mock-safe
  validation-focused unit tests plus the existing pipeline compatibility checks,
  and finish with `python3 -m compileall src tests`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A panel image that contains obvious internal subdivision is not
  silently accepted into the final comic package.
- **SC-002**: When the first attempt for a panel is rejected, the system makes
  a bounded retry using a stronger single-scene strategy without requiring the
  user to restart the whole run.
- **SC-003**: Metadata for a run with retries clearly shows requested attempts,
  rejected attempts, accepted attempts, and final panel status.
- **SC-004**: Existing mock-safe pipeline verification still produces a valid
  four-panel output package and final `1054x1054` comic after the feature is
  introduced.
- **SC-005**: Automated tests for validation and retry complete without network
  access or real provider credentials.

## Assumptions

- Single-panel validation may rely on deterministic heuristics, a mockable
  validator boundary, or another bounded internal mechanism, but the feature
  must not require live provider or network access in automated tests.
- Retry behavior should stay per-panel rather than rerunning the full comic by
  default.
- A failed validation result is considered a generation failure from the
  pipeline perspective, even if the provider returned an image file.
- Existing story planning and prompt generation will continue to provide the
  base scene specification; this feature adds acceptance control around panel
  image generation rather than replacing those stages.
