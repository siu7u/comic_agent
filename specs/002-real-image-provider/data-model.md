# Data Model: Real image provider integration

## ProviderSelection

**Purpose**: Captures which provider mode the run should use.

**Fields**:

- `provider_name`: stable user-facing provider identifier
- `provider_mode`: `mock` or `real`
- `requires_credentials`: whether environment validation is required before
  generation starts

**Validation Rules**:

- Must resolve to one supported provider
- Automated tests must be able to resolve explicitly to `mock` without relying
  on the CLI default

## ProviderConfiguration

**Purpose**: Represents the validated configuration required to initialize a
real image provider.

**Fields**:

- `provider_name`
- `credential_presence`: whether each required environment variable is present
- `configuration_valid`: overall validation result
- `missing_items`: list of missing or invalid setup inputs

**Validation Rules**:

- Must be validated before the first external provider request
- Must fail closed when required credentials are absent or empty
- Must not serialize secret values into metadata

## ProviderRunRecord

**Purpose**: Stores run-level provider execution traceability for metadata.

**Fields**:

- `provider_name`
- `provider_mode`
- `started_with_valid_config`
- `completed_successfully`
- `failure_message`

**Relationships**:

- One `ProviderRunRecord` belongs to one comic generation run
- One `ProviderRunRecord` summarizes many `PanelGenerationAttempt` records

## PanelGenerationAttempt

**Purpose**: Represents one panel's provider execution outcome.

**Fields**:

- `panel_index`
- `provider_name`
- `provider_mode`
- `retry_count`
- `succeeded`
- `failure_message`
- `image_artifact_available`
- `final_image_prompt`

**Validation Rules**:

- `panel_index` must map to one of the four required panels
- `retry_count` must stay within the current retry limit
- `failure_message` is required when `succeeded` is false
- `final_image_prompt` must describe exactly one full-frame single-scene image
- `final_image_prompt` must not include page-level layout instructions such as
  comic grids, split-screen directions, montage layouts, or four-panel framing

## CharacterBible

**Purpose**: Defines the subject identity that must remain visually consistent
across all four generated panels.

**Fields**:

- `summary`
- `appearance_traits`
- `personality_notes`
- `consistency_rules`

**Validation Rules**:

- `summary` should identify the subject, not restate the entire theme
- `appearance_traits` should contain concrete visual cues such as coat color,
  markings, silhouette, or stable accessories when inferable
- consistency rules must preserve recognizable identity across all panels

## StyleBible

**Purpose**: Defines rendering and tone guidance that is safe to send to a
single-image provider call.

**Fields**:

- `style_name`
- `tone`
- `composition_rules`
- `rendering_traits`

**Validation Rules**:

- Must not encode page-level or multi-panel layout instructions
- Must focus on rendering, tone, and single-scene composition guidance only

## StoryStructure Extension

**Purpose**: Represents the four-panel narrative plan before provider execution.

**Additional Rules**:

- For seasonal or time-progression themes, each panel must map to one distinct
  stage of progression
- Panel scene descriptions must remain single-scene and provider-safe

## MetadataRecord Extensions

**Purpose**: Extends the existing metadata payload without changing the output
artifact contract.

**Additional Fields**:

- `provider_mode`
- `provider_run`
- per-panel provider execution outcome fields

**Validation Rules**:

- Must preserve existing request, bible, story, prompt, and output-path fields
- Must record provider name for both mock and real runs
- Must preserve warnings and retry outcomes even when generation fails late
- Must preserve the exact provider-facing `final_image_prompt` used for each
  panel so regressions in prompt structure are inspectable

## DocumentationDeliverable

**Purpose**: Tracks README obligations for contributor-facing setup and usage.

**Fields**:

- `setup_instructions_present`
- `environment_variables_documented`
- `provider_selection_documented`
- `testing_boundary_documented`

**Validation Rules**:

- `README.md` must describe mock vs real provider behavior
- `README.md` must explain required environment setup for real provider use
- `README.md` must keep automated test expectations mock-first
