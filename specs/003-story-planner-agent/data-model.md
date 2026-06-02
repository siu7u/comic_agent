# Data Model: StoryPlannerAgent refactor

## StoryPlannerAgent

**Purpose**: Owns story planning for one comic request and produces exactly four
planned panel beats.

**Fields**:

- `normalized_theme`
- `subject`
- `intent_type`
- `planning_notes` (optional internal trace data only if needed)

**Validation Rules**:

- Must accept one comic request and return exactly one four-panel story
  structure
- Must not call external services or live models
- Must produce deterministic output for the same request input

## PlanningContext

**Purpose**: Represents the normalized input used to decide planning behavior.

**Fields**:

- `raw_theme`
- `normalized_theme`
- `explicit_character`
- `resolved_subject`
- `intent_keywords`
- `intent_type`

**Validation Rules**:

- `resolved_subject` uses `request.character` when provided
- `resolved_subject` falls back to inferred subject only when explicit
  character is absent
- `resolved_subject` must avoid long action phrases when a shorter subject is
  available

## StoryIntentType

**Purpose**: Captures the planning mode selected for a request.

**Allowed Values**:

- `seasonal_progression`
- `school_day`
- `competition_climax`
- `journey_growth`
- `fallback_gag`

**Validation Rules**:

- Exactly one intent type must be selected per request
- Intent selection must follow a stable deterministic priority when multiple
  intent keywords are present

## SubjectCandidate

**Purpose**: Represents a possible inferred subject identified from the theme.

**Fields**:

- `text`
- `specificity_rank`
- `matched_from`

**Validation Rules**:

- Higher-specificity candidates outrank generic candidates
- Generic animal or actor terms should be used only when no more specific
  candidate is available

## PlannedPanelBeat

**Purpose**: Represents one concrete story beat returned to the rest of the
pipeline.

**Fields**:

- `index`
- `caption`
- `dialogue`
- `scene_description`
- `visual_description`
- `action`
- `emotion`
- `camera_framing`

**Validation Rules**:

- Exactly four planned panel beats must exist
- Captions must be distinct within one story
- `scene_description` must be concrete and distinct across all four panels
- `visual_description` must not simply restate the full theme
- `action` must describe one panel-level action
- No field may include page-level layout instructions, multi-panel requests, or
  collage directions

## StoryStructure Compatibility

**Purpose**: Preserves the current downstream contract consumed by prompt
generation, providers, composition, and metadata export.

**Relationships**:

- One `StoryPlannerAgent` produces one `StoryStructure`
- One `StoryStructure` contains four `PlannedPanelBeat` values materialized as
  existing `PanelSpec` records

**Validation Rules**:

- Existing downstream fields remain present and usable
- A compatibility wrapper may delegate to the new planner but must preserve the
  same output shape

## DocumentationDeliverable

**Purpose**: Tracks whether contributor-facing architecture documentation needs
to change because of the refactor.

**Fields**:

- `readme_update_required`
- `architecture_description_updated`
- `workflow_notes_updated`

**Validation Rules**:

- `README.md` only changes when contributor-facing architecture or workflow
  wording materially changes
