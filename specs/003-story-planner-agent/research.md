# Research: StoryPlannerAgent refactor

## Decision 1: Introduce one internal StoryPlannerAgent with a compatibility wrapper

**Decision**: Add a lightweight internal `StoryPlannerAgent` with one clear
planning entrypoint and keep `build_story_structure(request)` as a compatibility
wrapper that delegates to the new planner.

**Rationale**: The feature is an internal architecture and planning-quality
refactor, not a CLI redesign. A dedicated planner object or equivalent
agent-like component improves readability and testability while keeping the
rest of the pipeline stable.

**Alternatives considered**:

- Keep expanding the current free functions in place: rejected because the
  planner logic is already growing beyond a simple template and needs a clearer
  responsibility boundary.
- Introduce an external multi-agent framework: rejected because the spec
  explicitly forbids external agent frameworks and live planning calls.

## Decision 2: Limit intent detection to a small deterministic rule set

**Decision**: Support exactly four planning modes in this feature: seasonal
progression, school-day or day-in-the-life, journey or transformation or
growth progression, and fallback gag-comic.

**Rationale**: The spec asks for a lightweight planner that solves currently
observed weak planning patterns without adding speculative natural-language
reasoning complexity. A narrow rule set keeps behavior deterministic and easy to
test.

**Alternatives considered**:

- Add many more intent categories now: rejected because broader taxonomy would
  increase ambiguity and test burden without being required.
- Use one generic planner for all themes: rejected because the current problem
  is precisely that generic planning produces repetitive scenes.

## Decision 3: Use explicit subject-priority matching before generic extraction

**Decision**: Subject extraction will first honor `request.character`, then
apply a deterministic priority list of more specific subject phrases before
falling back to generic animal or actor terms, and finally to `main character`
only when no better subject is found.

**Rationale**: The quality issue is not just intent detection; it is also weak
or overly broad subject inference. Prioritized matching prevents regressions
such as returning `小兔子上学` instead of `小兔子`.

**Alternatives considered**:

- Use only regex slicing from the full theme: rejected because it is too brittle
  for mixed Chinese phrases and action-heavy subjects.
- Depend entirely on explicit `--character`: rejected because the feature must
  improve planning for ordinary theme-only usage.

## Decision 4: Generate concrete panel beats from intent-specific scene templates

**Decision**: Each supported intent type will define four distinct panel beat
roles, captions, and concrete scene expectations, with fallback planning still
producing four distinct visual moments rather than repeating the same generic
theme sentence.

**Rationale**: The planning problem is visible in repeated scene descriptions.
Intent-specific beat templates are the smallest deterministic mechanism that
can reliably produce stronger scene diversity for downstream prompt generation.

**Alternatives considered**:

- Keep current repeated scene wording and vary only emotion or framing: rejected
  because it does not solve the weak-story problem.
- Let prompt generation invent distinct scenes later: rejected because story
  planning should own story progression and prompt generation should not absorb
  planning responsibilities.

## Decision 5: Preserve existing StoryStructure and PanelSpec contracts

**Decision**: Keep the current four-panel `StoryStructure` and `PanelSpec`
shape unchanged unless an additive planning-trace field becomes strictly
necessary during implementation.

**Rationale**: Prompt building, metadata export, mock generation, and provider
execution already depend on the current structure. Preserving the contract keeps
the refactor surgical and limits test fallout.

**Alternatives considered**:

- Redesign panel data around a richer planning graph: rejected because it would
  introduce unnecessary downstream churn.
- Move planning-specific outputs into metadata-only fields: rejected because the
  downstream pipeline already consumes the panel fields directly.

## Decision 6: Keep automated verification mock-safe and planner-focused

**Decision**: Validate the refactor with unit tests for intent detection,
subject extraction, and intent-specific planning, plus one compatibility test
that confirms `build_story_structure(request)` still returns a valid
`StoryStructure` consumable by the existing pipeline.

**Rationale**: The constitution requires deterministic, mock-safe verification.
This feature changes planning quality, not provider I/O, so tests should stay
local and fast.

**Alternatives considered**:

- Require live provider runs to validate planning quality: rejected because the
  feature is about deterministic planning logic and must not depend on network
  access.
- Skip compatibility coverage and rely only on unit tests: rejected because the
  wrapper contract is part of the stated acceptance criteria.
