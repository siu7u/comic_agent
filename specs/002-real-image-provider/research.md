# Research: Real image provider integration

## Decision 1: Add one explicit real provider implementation plus a simple selector

**Decision**: Add a single concrete real provider implementation for MVP
delivery and expose a minimal provider-selection input at the CLI level, while
retaining `MockImageProvider` as the default behavior for tests and local
development.

**Rationale**: The existing project already has a small provider abstraction and
one mock implementation. Extending that interface with one real provider keeps
the change surgical and avoids unnecessary registries or plugin systems.

**Alternatives considered**:

- Add multiple real providers now: rejected because the spec requires only one
  real provider and the constitution prohibits speculative provider expansion.
- Replace mock with real provider by default everywhere: rejected because tests
  must remain deterministic and credential-free.

## Decision 2: Use environment variables for credentials and fail fast before generation

**Decision**: Read provider credentials and any required configuration from
environment variables, validate them before the first provider call, and return
an actionable configuration error if setup is incomplete.

**Rationale**: Environment variables fit the existing CLI-only workflow and keep
secrets out of flags, files, and committed code. Early validation prevents
partial generation runs that fail only after work has already started.

**Alternatives considered**:

- Read credentials from CLI flags: rejected because it increases exposure of
  secrets in shell history and process listings.
- Read credentials from a project config file: rejected because it adds a new
  configuration surface not required by the current feature.

## Decision 3: Support text-to-image only in this feature

**Decision**: Real provider integration will send the existing final panel
prompt text as text-to-image requests only. Reference-image input remains within
the current MVP boundary and does not trigger real image-to-image behavior.

**Rationale**: The current story, prompt, metadata, and layout pipeline already
produces complete text prompts for each panel. Using that contract directly
keeps the integration narrow and avoids mixing in deferred scope.

**Alternatives considered**:

- Add real image-to-image now because reference images already exist in the
  request model: rejected because the feature spec explicitly defers it.
- Ignore reference-image input entirely during real-provider runs: rejected
  because the pipeline must preserve the existing request contract and metadata.

## Decision 4: Preserve pipeline shape and enrich metadata rather than redesign it

**Decision**: Keep the current generation flow intact: request parsing, safety,
story planning, prompt building, provider execution, composition, and export.
Extend metadata with run-level provider mode, provider name, panel retry
outcomes, and failure details as needed.

**Rationale**: The constitution requires a modular pipeline and surgical
changes. The pipeline already works end-to-end with mock output, so real
provider support should slot into the provider execution stage rather than
reshape upstream or downstream modules.

**Alternatives considered**:

- Introduce a new orchestration layer for provider lifecycle: rejected because
  the existing CLI flow is sufficient.
- Store provider execution state outside metadata: rejected because the spec
  explicitly calls for traceability in `metadata.json`.

## Decision 5: Keep automated tests mock-first and add provider integration tests with stubs

**Decision**: Continue using `MockImageProvider` for existing unit and
integration tests. Add new tests that validate provider selection, environment
validation, and error handling by stubbing the real provider boundary instead of
calling a live service.

**Rationale**: This satisfies the constitution's verifiability requirement and
keeps tests deterministic, fast, and free of paid API dependencies.

**Alternatives considered**:

- Run live provider calls in CI: rejected because credentials, cost, and
  network access would make the suite fragile.
- Skip provider-specific tests and rely only on manual runs: rejected because
  configuration and failure handling are core logic that should be tested.
