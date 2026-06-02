# Research: StoryboardAgent for four-panel story expansion

## Decision: Keep the feature deterministic and rule-based

**Rationale**: The specification explicitly requires no external LLM calls, no
provider dependency, and mock-safe automated verification. A deterministic
keyword- and rule-based agent keeps story expansion fast, predictable, and easy
to test.

**Alternatives considered**:

- LM-assisted story expansion: rejected because it adds runtime variability and
  dependency concerns that are out of scope for this feature.
- Provider-side story expansion: rejected because story structure should be
  decided before prompt generation and must remain provider-agnostic.

## Decision: LM-assisted mode should produce structured semantics, not full panel beats

**Rationale**: The repository already supports an LM-assisted planner.
Using that path to produce one semantic JSON object lets both planning modes
share the same StoryboardAgent expansion logic. This keeps downstream story
quality behavior consistent and avoids maintaining two different panel-planning
systems.

**Alternatives considered**:

- LM returns four full panel beats directly: rejected because it bypasses the
  StoryboardAgent and creates two separate planning behaviors.
- Rule-based-only semantics forever: rejected because the user explicitly wants
  stronger semantic understanding than the heuristic parser alone can provide.

## Decision: Introduce StoryboardAgent behind the existing compatibility entrypoint

**Rationale**: The current pipeline already expects a `StoryStructure`-shaped
result. Keeping `build_story_structure(request)` as the stable compatibility
entrypoint minimizes downstream churn while allowing the internal planning
implementation to change.

**Alternatives considered**:

- Replace all call sites with a new public API immediately: rejected because it
  creates unnecessary migration work for no user-facing benefit.
- Keep the current planner as-is and add helper functions around it: rejected
  because it does not create a clear ownership boundary for story expansion.

## Decision: Detect one storyboard structure per request using a stable priority order

**Rationale**: Some prompts naturally contain overlapping cues. The planner
must still return one deterministic four-panel structure. A documented priority
order avoids ambiguity and keeps the output stable across runs.

**Alternatives considered**:

- Allow multiple structures to mix in one story: rejected because it weakens
  panel distinctness and increases the chance of multi-scene prompts.
- Ask the user to disambiguate every mixed prompt: rejected because the feature
  should improve the default single-command workflow.

## Decision: Supported structure set is narrow and explicit

**Rationale**: The specification names day-in-the-life, seasonal progression,
journey or adventure, problem solving, and fallback. Constraining the first
version to this set keeps the planner understandable and avoids speculative
intent classes.

**Alternatives considered**:

- Broader ontology of many story types: rejected because it adds complexity
  without being required by the feature.
- Only one generic fallback structure: rejected because it fails the core goal
  of improving story expansion quality for common prompt types.

## Decision: Subject extraction uses explicit override first, then specific-to-generic keyword priority

**Rationale**: Subject stability is foundational for both story clarity and
downstream character consistency. Using `--character` as the highest-priority
source and then applying specific-to-generic keyword rules satisfies the
specification and avoids action-heavy subject strings.

**Alternatives considered**:

- Pure regex extraction only: rejected because it can easily return long action
  phrases instead of stable character subjects.
- Generic noun fallback before specific phrase search: rejected because it
  would collapse `流浪橘猫` into `猫` too often.

## Decision: Expand panel beats as concrete visual moments, not abstract story labels

**Rationale**: The current problem is not a lack of four panels but a lack of
distinct, image-friendly moments. Each panel beat must therefore include a
visually specific scene description, action, emotion, and framing suited for
downstream image prompt generation.

**Alternatives considered**:

- Reuse generic phrases like `encounters the setup`: rejected because they do
  not constrain or improve the visual story.
- Push concreteness entirely into prompt generation: rejected because prompt
  generation should translate storyboard intent, not invent the story structure.

## Decision: Keep page-level layout restrictions at the story-expansion layer

**Rationale**: If storyboard output already avoids `grid`, `comic page`,
`four-panel layout`, and similar language, downstream prompts are less likely to
reintroduce full-page or multi-scene instructions.

**Alternatives considered**:

- Let prompt generation strip layout terms later: rejected because weak story
  structure would still leak layout-like concepts downstream.
- Leave layout avoidance entirely to provider-specific prompt handling:
  rejected because this feature is specifically about improving pre-prompt story
  expansion quality.

## Decision: Verification remains mock-safe and regression-driven

**Rationale**: The feature affects planning quality and compatibility, so the
most valuable tests are deterministic unit tests for structure detection and
panel expansion plus mock-provider pipeline checks.

**Alternatives considered**:

- Live provider verification: rejected because the specification explicitly
  excludes network and credential requirements.
- Prompt-only verification without planner tests: rejected because the feature
  changes story expansion first and foremost.
