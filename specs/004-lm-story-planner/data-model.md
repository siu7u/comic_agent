# Data Model: LM-assisted story planner

## PlannerSelectionMode

**Purpose**: Represents the planner mode requested for one CLI run.

**Allowed Values**:

- `rule_based`
- `lm_assisted`

**Validation Rules**:

- `rule_based` remains the default mode
- `lm_assisted` is selected only through an explicit CLI flag

## LMConfiguration

**Purpose**: Represents the runtime configuration required for manual
LM-assisted planning.

**Fields**:

- `credentials_present`
- `endpoint_config_present`
- `configuration_valid`
- `missing_items`

**Validation Rules**:

- Configuration is read from environment variables
- Missing or invalid LM configuration must not break the fallback rule-based
  planner path
- Secret values must not be written into metadata

## LMPlanningPayload

**Purpose**: Represents the raw strict JSON planning object returned by the LM.

**Fields**:

- `subject`
- `intent_type`
- `panels`

**Validation Rules**:

- Must be one strict JSON object
- Must define exactly four panels
- Must be schema-valid before conversion into a story structure

## ValidatedPlanningResult

**Purpose**: Represents an LM planning result that passed schema and content
validation.

**Fields**:

- `subject`
- `intent_type`
- `panel_beats`
- `source_mode`

**Validation Rules**:

- Must preserve explicit `request.character` as authoritative when provided
- Must include all required panel fields
- Must not include page-level layout or multi-panel directions

## PlannerExecutionRecord

**Purpose**: Captures run-level traceability for planner selection and fallback.

**Fields**:

- `requested_mode`
- `actual_mode`
- `fallback_triggered`
- `fallback_reason`

**Validation Rules**:

- Must record both requested and actual planner mode
- `fallback_reason` is required when fallback is triggered

## StoryStructure Compatibility

**Purpose**: Preserves the current downstream planning contract after either
rule-based or LM-assisted planning succeeds.

**Relationships**:

- One planner selection produces one actual planning path
- One validated LM planning result or one fallback rule-based result produces
  one `StoryStructure`

**Validation Rules**:

- The final output to the rest of the pipeline remains a four-panel
  `StoryStructure`
- Downstream prompt generation, metadata export, and composition continue to
  consume the same panel fields

## DocumentationDeliverable

**Purpose**: Tracks the required contributor and user documentation updates for
planner selection and setup.

**Fields**:

- `planner_flag_documented`
- `lm_environment_setup_documented`
- `fallback_behavior_documented`
- `testing_boundary_documented`

**Validation Rules**:

- `README.md` must explain the planner-selection flag
- `README.md` must explain environment-based LM configuration for manual runs
- `README.md` must explain that automated tests stay mock-safe
