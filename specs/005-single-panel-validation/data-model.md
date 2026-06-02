# Data Model: Single-panel generation validation and retry

## PanelGenerationAttempt

**Purpose**: Represents one provider-backed attempt to generate one panel image.

**Fields**:

- `panel_index`
- `attempt_number`
- `strategy_name`
- `provider_name`
- `provider_mode`
- `generated_image_available`
- `prompt_source_summary`

**Validation Rules**:

- Attempts are ordered and bounded per panel
- Each attempt belongs to exactly one panel
- A provider-returned image does not imply the attempt is accepted

## SinglePanelValidationResult

**Purpose**: Captures whether one generated image satisfies the single-panel
acceptance contract.

**Fields**:

- `decision`
- `reason`
- `validator_name`
- `validator_mode`

**Allowed Values**:

- `accepted`
- `rejected`
- `ambiguous`

**Validation Rules**:

- Every attempt receives exactly one validation result
- `reason` is required when the decision is not `accepted`

## RetryStrategyProfile

**Purpose**: Defines the named generation strategy used for the initial attempt
or later retries.

**Fields**:

- `name`
- `attempt_order`
- `constraint_strength`
- `prompt_adjustment_scope`

**Validation Rules**:

- Strategy order is deterministic
- Strategy progression is bounded
- Later strategies are equal or stronger in single-scene strictness

## PanelAttemptTrace

**Purpose**: Combines attempt metadata, validation outcome, and final status for
one panel.

**Fields**:

- `attempts`
- `accepted_attempt_number`
- `final_status`
- `failure_reason`

**Allowed Values**:

- `accepted`
- `failed_validation`
- `failed_generation`

**Validation Rules**:

- Exactly one final status exists per panel
- `accepted_attempt_number` is present only when the panel is accepted
- `failure_reason` is required when final status is not `accepted`

## AcceptedPanelArtifact

**Purpose**: Represents the panel image selected for final composition after all
validation and retry logic completes.

**Fields**:

- `panel_index`
- `image_path`
- `accepted_attempt_number`

**Validation Rules**:

- There is at most one accepted artifact per panel
- Only accepted panel artifacts may be passed into final composition

## StoryStructure Compatibility

**Purpose**: Preserves the current downstream story contract while adding
attempt-level image acceptance control.

**Relationships**:

- One `StoryStructure` still defines four planned panels
- One planned panel maps to one `PanelAttemptTrace`
- One `PanelAttemptTrace` may contain multiple `PanelGenerationAttempt` records
  but only zero or one `AcceptedPanelArtifact`

**Validation Rules**:

- Story planning remains upstream of image validation
- Final composition still consumes exactly four accepted panel images for a
  successful run

## DocumentationDeliverable

**Purpose**: Tracks required contributor-facing documentation changes for
validation and retry behavior.

**Fields**:

- `readme_update_required`
- `validation_trace_documented`
- `retry_behavior_documented`
- `debugging_notes_documented`

**Validation Rules**:

- `README.md` must explain how validation and retries affect metadata
- `README.md` must explain that automated verification remains mock-safe
