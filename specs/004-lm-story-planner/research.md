# Research: LM-assisted story planner

## Decision 1: Keep rule-based planning as the default and add LM planning only through an explicit CLI flag

**Decision**: The existing rule-based `StoryPlannerAgent` remains the default
planner. LM-assisted planning is enabled only when the user explicitly selects
it through a per-run CLI flag.

**Rationale**: This isolates risk, preserves today’s stable behavior, and lets
contributors compare LM-assisted results against the deterministic baseline
without changing every ordinary run.

**Alternatives considered**:

- Make LM-assisted planning the default with fallback: rejected because the
  feature is intended as a controlled experiment rather than a global behavior
  switch.
- Use environment variables or config files to select planner mode: rejected
  because planner selection is a run-level product choice and should be visible
  at invocation time.

## Decision 2: Require one strict JSON planning payload from the LM

**Decision**: The LM-assisted planner will accept only one strict JSON object
as the planning result.

**Rationale**: A strict JSON boundary provides the cleanest validation surface,
keeps parsing simple, and minimizes ambiguity before fallback decisions.

**Alternatives considered**:

- Parse free-form text heuristically: rejected because it would weaken
  determinism and complicate validation.
- Accept code-fenced or loosely formatted JSON: rejected because a strict JSON
  boundary is easier to validate and test.

## Decision 3: Validate LM output aggressively and fall back automatically

**Decision**: The system validates panel count, required fields, subject
handling, and single-scene constraints before accepting LM output. Any
validation failure triggers automatic fallback to the rule-based planner.

**Rationale**: The existing comic pipeline expects a clean four-panel story
structure. Validation plus fallback keeps the rest of the pipeline insulated
from LM instability.

**Alternatives considered**:

- Partially repair invalid LM output: rejected because repair logic would add
  complexity and ambiguity to an experimental integration.
- Fail the whole run on LM invalidity: rejected because the spec requires safe
  fallback to the deterministic planner.

## Decision 4: Use environment variables for LM configuration

**Decision**: Any credentials or endpoint configuration required for manual
LM-assisted planning runs will be read from environment variables.

**Rationale**: This matches the project’s current real-provider setup style and
keeps secrets out of CLI arguments and committed configuration.

**Alternatives considered**:

- Put LM configuration in CLI arguments: rejected because it exposes sensitive
  details in shell history and process listings.
- Use repository or local config files: rejected because the spec selected an
  environment-based configuration model.

## Decision 5: Record both requested and actual planner mode in metadata

**Decision**: Run-level traceability will include both the planner mode the
user requested and the planner that ultimately produced the story after any
fallback.

**Rationale**: This makes fallback behavior observable, supports comparisons
between rule-based and LM-assisted planning, and avoids ambiguity when a run
requests LM planning but ends up using the deterministic fallback.

**Alternatives considered**:

- Record only whether LM was requested: rejected because it hides fallback
  outcomes.
- Record only the final planner used: rejected because it loses the user’s
  original intent for the run.

## Decision 6: Keep all automated verification mock-safe

**Decision**: Automated tests will use mocked or stubbed LM responses for valid
results, malformed results, unavailable planner conditions, and fallback paths.

**Rationale**: The constitution requires deterministic tests, and this feature
changes planning orchestration rather than requiring live provider or live model
verification in CI.

**Alternatives considered**:

- Use live LM calls in automated tests: rejected because of network, cost, and
  determinism concerns.
- Skip fallback testing and rely on manual experimentation: rejected because
  fallback behavior is a core feature requirement.
