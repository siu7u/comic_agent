# Research: Single-panel generation validation and retry

## Decision 1: Add a separate panel validator instead of embedding acceptance rules inside providers

**Decision**: Introduce an internal single-panel validation boundary after each
provider attempt rather than teaching each provider to decide whether its own
output is acceptable.

**Rationale**: The current failure is a pipeline-level quality failure, not a
transport failure. Keeping validation separate preserves a minimal provider
interface and lets the same acceptance rule apply to mock and real providers.

**Alternatives considered**:

- Push validation into `WanxImageProvider`: rejected because the problem is not
  Wanx-specific and would over-couple provider code to output policy.
- Accept provider output blindly and rely only on prompt changes: rejected
  because prompt-only control has already shown instability.

## Decision 2: Model panel generation as bounded attempts with strategy progression

**Decision**: Treat each panel as a bounded series of attempts, each using a
named retry strategy profile that can strengthen single-scene constraints when
validation fails.

**Rationale**: A deterministic strategy ladder gives the system a recovery path
without needing the user to rerun the whole comic or relying on identical
retries.

**Alternatives considered**:

- Retry with the exact same prompt repeatedly: rejected because it gives weak
  recovery value and poor traceability.
- Retry the whole comic when one panel fails: rejected because the failure is
  panel-local and the cost is unnecessarily high.

## Decision 3: Keep automated validation mock-safe behind a validator boundary

**Decision**: Define a validator boundary that can be backed by deterministic
heuristics or a runtime-specific implementation, but require tests to exercise
the feature with mocked validation outcomes.

**Rationale**: The constitution requires deterministic tests without network
access. The feature is about orchestration and acceptance flow, so mocked
validation results are sufficient for automated coverage.

**Alternatives considered**:

- Require a live vision model or remote classifier in tests: rejected because
  it breaks deterministic offline testing.
- Hard-code one concrete heuristic implementation in the spec: rejected because
  the spec should describe behavior, not force one implementation tactic.

## Decision 4: Record panel-attempt traces in metadata

**Decision**: Extend metadata to record attempt-level strategy usage,
validation decisions, rejection reasons, and final accepted-or-failed status per
panel.

**Rationale**: The current debugging problem is opaque without attempt-level
traceability. Metadata must explain whether an image was provider-successful but
validator-rejected.

**Alternatives considered**:

- Record only final panel success/failure: rejected because it hides retry and
  rejection behavior.
- Use logs only: rejected because logs are not exported alongside the comic
  artifact set.

## Decision 5: Preserve composition and final layout contracts

**Decision**: The final `1054x1054` composition stage remains unchanged.
Validation and retry happen entirely before a panel is admitted to composition.

**Rationale**: The bug is not in the final layout code. Keeping composition
stable narrows risk and simplifies rollout.

**Alternatives considered**:

- Add post-composition repair or cropping logic: rejected because the current
  failure is best handled before bad inputs reach composition.
