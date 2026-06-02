# Data Model: StoryboardAgent for four-panel story expansion

## StoryboardAgent

**Purpose**: Internal planner responsible for converting a `ComicRequest` into a
deterministic four-panel `StoryStructure`.

**Fields / Responsibilities**:

- planning entrypoint
- story type detection
- subject resolution
- panel beat expansion
- compatibility delegation

**Validation Rules**:

- Must always return exactly four panels
- Must not require external network or provider access
- Must preserve compatibility with the current story contract

## StoryType

**Purpose**: Represents the detected structural pattern used to expand a prompt
into four storyboard stages.

**Allowed Values**:

- `day_in_the_life`
- `seasonal_progression`
- `journey_adventure`
- `problem_solving`
- `fallback_story`

**Validation Rules**:

- Exactly one story type is selected per request
- Selection is deterministic
- Fallback is used only when no stronger structure is detected

## SubjectResolution

**Purpose**: Captures the resolved main subject that anchors all four panels.

**Fields**:

- `source`
- `value`
- `normalized_value`

**Allowed Sources**:

- `explicit_character`
- `theme_inference`
- `fallback_default`

**Validation Rules**:

- Explicit character override wins when present
- The resolved value should avoid action-heavy phrases when a shorter stable
  subject is available
- If no subject is inferred, the normalized value becomes `main character`

## ThemeSemantics

**Purpose**: Shared semantic layer consumed by the StoryboardAgent before it
expands panel beats.

**Fields**:

- `subject`
- `activity`
- `primary_object`
- `setting_hint`
- `temporal_cues`
- `domain_cues`
- `source`

**Allowed Sources**:

- `rule_based`
- `lm_assisted`

**Validation Rules**:

- The semantic shape must remain stable across rule-based and LM-assisted modes
- Layout or multi-panel instructions are invalid semantic content
- Storyboard expansion uses one semantic result per request

## StoryStructure

**Purpose**: Existing pipeline-facing story result consumed by prompt
generation, metadata export, and panel image generation.

**Fields**:

- `title`
- `premise`
- `subject`
- `panels`

**Validation Rules**:

- `panels` must contain exactly four ordered panel story beats
- `subject` should remain stable across the four panels
- Output shape must stay compatible with the existing pipeline contract

## PanelStoryBeat

**Purpose**: One concrete storyboard moment intended to drive one downstream
image prompt and one final panel image.

**Fields**:

- `index`
- `caption`
- `dialogue`
- `scene_description`
- `action`
- `emotion`
- `camera_framing`
- `visual_description`

**Validation Rules**:

- Every field is required in the planner output
- `scene_description` must be concrete, visual, and distinct from the other
  three panels
- `action` must describe one panel-level action, not a whole story arc
- `visual_description` must not simply repeat the raw theme
- No panel beat may request a full comic page, grid, split-screen, or multiple
  scenes in one image

## StoryboardPattern

**Purpose**: Defines the expected four-stage sequence used for a recognized
story type.

**Fields**:

- `story_type`
- `captions`
- `stage_goals`
- `emotion_progression`
- `default_framing_pattern`

**Validation Rules**:

- Each supported story type maps to exactly four stage captions
- Stage sequence must remain ordered and deterministic
- Pattern content must produce image-friendly single-scene beats

## DocumentationDeliverable

**Purpose**: Tracks whether contributor-facing documentation must be updated.

**Fields**:

- `readme_update_required`
- `architecture_wording_changed`
- `workflow_wording_changed`

**Validation Rules**:

- `README.md` changes only when architecture or contributor workflow wording
  actually changes
- Internal-only implementation changes do not require unnecessary README churn
