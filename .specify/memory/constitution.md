<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- Template Principle 1 -> I. Spec-First Delivery
- Template Principle 2 -> II. CLI MVP and Simplicity
- Template Principle 3 -> III. Surgical Changes
- Template Principle 4 -> IV. Modular Comic Pipeline
- Template Principle 5 -> V. Verifiable Core Logic
- Added VI. Minimal Provider Abstraction
- Added VII. Character and Style Consistency
- Added VIII. Safety Before Generation
- Added IX. Real Command Verification
- Added X. No Speculative Features
Added sections:
- Operational Constraints
- Delivery Workflow and Quality Gates
Removed sections:
- None
Templates requiring updates:
- ⚠ pending .specify/templates/plan-template.md
- ⚠ pending .specify/templates/spec-template.md
- ⚠ pending .specify/templates/tasks-template.md
- ⚠ pending .specify/templates/commands/*.md (directory not present in this repository)
- ✅ reviewed CLAUDE.md
Follow-up TODOs:
- None
-->
# Comic Agent Constitution

## Core Principles

### I. Spec-First Delivery
Every feature MUST begin with a completed `spec.md`, `plan.md`, and `tasks.md`
before implementation starts. If scope, acceptance criteria, or task boundaries
are unclear, implementation MUST stop until those artifacts are updated. This
keeps the agent aligned with explicit requirements rather than inferred intent.

### II. CLI MVP and Simplicity
The project MUST deliver a command-line MVP before any web UI, database, queue,
or complex agent framework is introduced. New work MUST prefer the smallest
design that satisfies the current spec, and complexity MUST be justified in the
implementation plan's complexity tracking section. This protects delivery speed
and keeps the system easy to reason about.

### III. Surgical Changes
Changes MUST be limited to files and code paths directly required by the active
task. Refactors, cleanups, or style edits outside the requested scope MUST not
be bundled into feature work unless the spec explicitly includes them. This
preserves review clarity and reduces accidental regressions.

### IV. Modular Comic Pipeline
The implementation MUST separate story planning, panel prompt generation, image
provider execution, layout composition, and export into distinct modules with
clear interfaces. Cross-stage coupling that prevents isolated testing or module
replacement MUST be rejected. This ensures the four-panel comic pipeline stays
composable and maintainable.

### V. Verifiable Core Logic
Core logic MUST be testable with `pytest`, and tests MUST cover story planning,
prompt generation, layout composition, export metadata, and safety decisions as
applicable to the feature. External image APIs MUST be mocked in tests rather
than called directly. This keeps correctness checks fast, deterministic, and
safe to run in development.

### VI. Minimal Provider Abstraction
The codebase MUST define a simple image provider interface and MUST start with
`MockImageProvider` as the default implementation for development and tests.
Provider abstractions MUST remain minimal and task-driven; speculative support
for multiple backends, retries, orchestration layers, or provider registries is
prohibited unless required by the current spec. This allows extension without
premature framework design.

### VII. Character and Style Consistency
Comic generation MUST maintain a character bible and a style bible that are
available to each panel-generation step. Features that affect visual output MUST
preserve consistent characters, tone, and style across all four panels and MUST
record the relevant consistency inputs in metadata. This is required for the
project's core output quality.

### VIII. Safety Before Generation
Unsafe image requests MUST be rejected or rewritten before any generation call
is made. Safety behavior MUST be explicit in specs, test cases, and metadata
when a request is transformed or refused. This prevents the pipeline from
passing unsafe prompts to downstream providers.

### IX. Real Command Verification
After implementation, the smallest relevant real verification command MUST be
run, such as a targeted `pytest` invocation, type check, lint, or CLI demo.
Work is not complete until at least one appropriate command has been executed or
an environment constraint has been documented. This principle keeps completion
claims tied to observable results.

### X. No Speculative Features
The project MUST not add capabilities that are not required by the current spec.
Out-of-scope ideas such as web dashboards, persistent job queues, advanced
multi-agent orchestration, or provider-specific optimizations MUST remain out of
the implementation until they are explicitly specified. This enforces MVP
discipline and avoids dead abstractions.

### XI. Documentation Stays Aligned
`README.md` is part of the product contract and MUST be updated in the same
change whenever implementation changes affect CLI usage, configuration, project
structure, output files, metadata format, setup steps, provider behavior, or
test commands. Purely internal refactors that do not affect users or
contributors MUST NOT trigger README churn. README requirements are a
documentation deliverable, not a runtime feature.

## Operational Constraints

- The MVP output MUST include story structure, per-panel image prompts, generated
  panel images, a composed 2x2 final comic image, and metadata JSON.
- Provider-dependent behavior MUST be isolated so the pipeline can run with
  mocked providers during tests and local development.
- Safety checks, character bible data, and style bible data MUST be available
  before panel image generation begins.
- Metadata exports MUST be sufficient to trace the story plan, panel prompts,
  provider used, safety action taken, and composition inputs for each run.
- The repository MUST include a `README.md` that documents installation or
  preparation, CLI usage, arguments, example commands, output files, module
  responsibilities, provider boundaries, reference-image handling, and test
  execution for the current MVP.

## Delivery Workflow and Quality Gates

- Specifications MUST define user stories, safety expectations, output artifacts,
  and explicit out-of-scope items before planning begins.
- Plans MUST include a constitution check covering CLI-first scope, modular
  pipeline boundaries, testability, provider abstraction limits, consistency
  handling, and post-change verification.
- Tasks MUST include work for tests whenever core logic changes, MUST call out
  mock-based provider testing for external image generation paths, and MUST end
  with a concrete verification task.
- Tasks MUST include README creation or README update work whenever a feature
  changes user-facing CLI behavior, setup expectations, output artifacts,
  provider behavior, or test commands.
- Reviews MUST reject work that bypasses the spec-plan-tasks sequence or adds
  architecture beyond the current requirement set.

## Governance

This constitution overrides conflicting local process guidance for this
repository. Amendments MUST be made by updating this document together with any
affected templates and guidance files, and each amendment MUST include a sync
impact report at the top of the constitution. Versioning follows semantic
versioning for governance: MAJOR for incompatible principle changes or removals,
MINOR for new principles or materially expanded requirements, and PATCH for
clarifications that do not change project obligations. Compliance review MUST
occur during specification, planning, task generation, code review, and final
verification, with any justified exception recorded in the relevant plan or
review artifact.

**Version**: 1.1.0 | **Ratified**: 2026-05-28 | **Last Amended**: 2026-05-28
