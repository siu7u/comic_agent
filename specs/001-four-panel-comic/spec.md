# Feature Specification: Four-panel comic generation MVP

**Feature Branch**: `[001-four-panel-comic]`  
**Created**: 2026-05-28  
**Status**: Draft  
**Input**: User description: "Create a feature specification for the MVP of a text-to-image and image-to-image four-panel comic agent."

## Clarifications

### Session 2026-05-28

- Q: What fixed image format, panel size, final comic size, layout geometry, panel order, and MVP text-rendering rule should this feature use? → A: Use PNG; each panel is 512x512; final comic is 1054x1054; fixed 2x2 grid; left-to-right then top-to-bottom order; a visible 10px outer border plus 10px vertical and horizontal dividers on the final canvas; captions and dialogue stay in metadata.json only for MVP.
- Q: What prompt-input and reference-image inputs should the MVP support, and how should missing or user-provided panel prompts be handled? → A: Allow --image-prompt and --panel-prompt-1 through --panel-prompt-4; generate any missing panel prompts from the story plus shared bibles; merge user-provided prompts with generated prompts instead of replacing them; accept one global --reference-image; defer per-panel reference images; use the reference image only for validation and metadata in the MVP.
- Q: How should character_bible and style_bible be handled, and what should happen when user-provided prompt text conflicts with shared consistency rules? → A: Generate character_bible and style_bible automatically from theme, style, character, and prompt inputs; include both in every final panel prompt; rewrite user-provided prompt guidance as needed to include the shared bibles and resolve conflicts minimally; record rewrites and warnings in metadata.
- Q: What safety behavior should apply to theme input, prompt guidance, and reference images in the MVP? → A: Reject unsafe theme input before story generation; reject or minimally rewrite unsafe global or per-panel prompt guidance according to the safety policy; for reference images in the MVP, validate only file existence and supported image type, not visual safety content.
- Q: What CLI surface, metadata fields, mock-provider behavior, real-provider boundary, and MVP verification scope should this feature adopt? → A: Support one CLI command with --theme, --style, --character, --image-prompt, --panel-prompt-1 through --panel-prompt-4, --reference-image, --lang, and --out; store request fields, prompt_source, rewritten prompts, warnings, reference_image_path, provider name, and retry count in metadata.json; implement only MockImageProvider in this MVP; make mock images deterministic placeholders showing panel index and short caption and whether the request used text-only or reference-image input; defer real providers, API keys, provider selection, and non-mock retry policy; require tests for prompt merging, missing-panel prompt generation, reference-image validation/storage, 2x2 layout, mock pipeline, and metadata recording.
- Q: What documentation artifact must accompany this MVP, and how should it be treated in scope? → A: README.md is a documentation deliverable, not a runtime feature; it must explain installation/setup, CLI usage, arguments, example commands, expected outputs, project design, MockImageProvider-only MVP scope, reference-image handling, and test execution.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a complete comic (Priority: P1)

As a creator, I want to provide a comic theme or story idea and receive a
complete four-panel comic package so that I can review a coherent comic result
from a single command.

**Why this priority**: This is the core value of the feature. Without end-to-end
comic generation, the MVP does not deliver a usable outcome.

**Independent Test**: Run the generation command with a valid theme and confirm
that the system produces a four-panel story, four panel images, one composed
comic image, and a metadata file in the selected output directory.

**Acceptance Scenarios**:

1. **Given** a user provides a theme or story idea, **When** generation runs
   successfully, **Then** the system produces exactly four panels, one final 2x2
   comic image, and one metadata file in the output directory.
2. **Given** a user provides optional style and character details, **When**
   generation runs, **Then** the story, prompts, and output artifacts reflect
   those details consistently across all four panels.

---

### User Story 2 - Guide panel visuals (Priority: P2)

As a creator, I want to provide global prompt guidance, per-panel prompt
guidance, and an optional reference image so that I can steer the visual result
without manually writing the entire comic from scratch.

**Why this priority**: Guided visual control is the main differentiator between
basic story generation and a usable comic-creation workflow.

**Independent Test**: Run the generation command with image prompt guidance,
per-panel prompt guidance, and a readable reference image, then confirm that the
resulting panel prompts and metadata reflect those inputs.

**Acceptance Scenarios**:

1. **Given** a user provides global image prompt guidance, **When** the system
   builds the four panel prompts, **Then** each panel prompt incorporates that
   guidance while preserving the panel's story role.
2. **Given** a user provides prompt guidance for one or more specific panels,
   **When** the system builds prompts for those panels, **Then** the supplied
   guidance is treated as strong direction and the metadata records which panels
   used direct user input.
3. **Given** a user provides a valid reference image for image-guided
   generation, **When** the request is processed, **Then** the metadata records
   that the request used reference imagery as part of the generation inputs.

---

### User Story 3 - Receive safe and transparent adjustments (Priority: P3)

As a creator, I want unsafe or conflicting requests to be rejected or minimally
adjusted with a clear record of what changed so that I understand why the system
modified or refused part of my input.

**Why this priority**: Safety and traceability protect the user experience and
keep the output pipeline predictable when prompt guidance conflicts with story or
policy constraints.

**Independent Test**: Run the generation command with conflicting or unsafe
prompt guidance and confirm that the system either rejects the request with a
clear explanation or completes the run with metadata describing each adjustment.

**Acceptance Scenarios**:

1. **Given** a user provides prompt guidance that conflicts with the story,
   shared character details, or safety policy, **When** the system processes the
   request, **Then** it rewrites the conflicting prompt portion minimally and
   records the adjustment in metadata.
2. **Given** a user provides unsafe content, **When** the system evaluates the
   request, **Then** it rejects or rewrites the request according to the safety
   policy before image generation occurs.

### Edge Cases

- The system rejects the request with a clear error when the required theme or
  story idea is missing.
- The system creates the output directory automatically when the selected
  directory does not already exist.
- The system stops with a clear error when a provided reference image path cannot
  be read.
- The system stops before story generation when the theme input is unsafe.
- The system retries a failed panel image generation step up to two times before
  surfacing failure information to the user.
- The system still writes failure metadata when a panel cannot be generated after
  the allowed retries.
- The system preserves the four-panel structure even when user prompt guidance is
  missing for some or all panels.
- The final comic canvas uses a fixed 2x2 layout with panel order left-to-right,
  top-to-bottom and a uniform 10-pixel outer border and center dividers.
- The MVP validates reference-image file existence and supported image type, but
  does not classify image content for safety.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a required comic theme or story idea as the
  minimum input for a generation request.
- **FR-002**: The system MUST accept optional visual style, main character
  description, global image prompt guidance, per-panel image prompt guidance,
  reference image input, output language, and output directory values.
- **FR-003**: The MVP MUST support a single global image prompt guidance input
  and optional per-panel prompt guidance inputs for panels 1 through 4.
- **FR-004**: When per-panel prompt guidance is missing for one or more panels,
  the system MUST generate the missing panel prompts from the story structure
  plus shared character and style guidance.
- **FR-005**: When users provide global or per-panel prompt guidance, the
  system MUST merge that guidance into generated panel prompts rather than
  treating user-provided text as a complete replacement.
- **FR-006**: The MVP MUST accept a single global reference image input for the
  whole comic request and MUST defer per-panel reference image inputs to a later
  feature.
- **FR-007**: The system MUST generate exactly four story panels for every
  successful request.
- **FR-008**: The system MUST produce for each panel an index, caption,
  dialogue, scene description, action, emotion, camera or framing direction, and
  final image prompt.
- **FR-009**: The system MUST maintain shared character and style guidance across
  all four panels and include those shared details in every final panel prompt.
- **FR-010**: The system MUST generate a `character_bible` and a `style_bible`
  automatically from the request's theme, style, character, and prompt inputs.
- **FR-011**: The system MUST incorporate user-provided global image prompt
  guidance into each final panel prompt while preserving the panel's role in the
  story structure.
- **FR-012**: The system MUST incorporate both `character_bible` and
  `style_bible` into every final panel prompt.
- **FR-013**: The system MUST treat user-provided global or per-panel prompt
  guidance as subject to minimal rewriting when needed to restore shared
  character consistency, style consistency, or story alignment.
- **FR-014**: The system MUST record prompt rewrites and resulting warnings in
  metadata whenever shared consistency rules or safety rules require an
  adjustment.
- **FR-015**: The system MUST treat user-provided per-panel image prompts as
  strong guidance for the corresponding panels unless those prompts conflict with
  story consistency or safety constraints.
- **FR-016**: The system MUST generate panel prompts from the story structure,
  shared character details, and shared style details when user prompt guidance
  is absent.
- **FR-017**: The system MUST ensure every final panel prompt contains character,
  scene, action, emotion, camera or framing, style, and consistency details.
- **FR-018**: The system MUST reject or minimally rewrite unsafe or conflicting
  requests before image generation and MUST record the reason for rejection or
  adjustment in metadata.
- **FR-019**: The system MUST reject unsafe theme input before story generation
  begins.
- **FR-020**: The system MUST support both text-only requests and requests that
  include a readable global reference image as an additional generation input.
- **FR-021**: The system MUST reject or minimally rewrite unsafe global
  image-prompt guidance and unsafe per-panel prompt guidance according to the
  safety policy.
- **FR-022**: The MVP MUST validate and record the global reference image but
  MUST NOT require the mock generation path to perform real image-to-image
  transformation.
- **FR-023**: The MVP MUST validate only reference-image file existence and
  supported image type, and MUST NOT perform visual safety classification on
  reference-image content in this feature.
- **FR-024**: The system MUST generate four panel image files and one final comic
  image arranged as a 2x2 grid for every successful request.
- **FR-025**: The system MUST generate each panel image as a 512x512 PNG file.
- **FR-026**: The system MUST generate the final comic image as a 1054x1054 PNG
  file with a fixed 2x2 layout, using a 10-pixel outer border and 10-pixel
  vertical and horizontal dividers on the final canvas.
- **FR-027**: The system MUST place panels in left-to-right, top-to-bottom
  order, with panel 1 at the top-left, panel 2 at the top-right, panel 3 at the
  bottom-left, and panel 4 at the bottom-right.
- **FR-028**: The MVP MUST NOT render captions or dialogue into panel images or
  the final comic image; captions and dialogue MUST be stored in metadata only.
- **FR-029**: The system MUST save a metadata file that includes the original
  request, story structure, per-panel content, prompt sources, image file paths,
  prompt adjustments, and final comic image path.
- **FR-030**: The system MUST expose a single CLI command that accepts `--theme`,
  optional `--style`, `--character`, `--image-prompt`, `--panel-prompt-1`
  through `--panel-prompt-4`, optional `--reference-image`, optional `--lang`,
  and optional `--out`.
- **FR-031**: The metadata file MUST store request fields, per-panel
  `prompt_source`, rewritten prompts, warnings, `reference_image_path`,
  provider name, and retry count for each generated panel.
- **FR-032**: `prompt_source` values in metadata MUST distinguish generated
  prompts from merged user-guided prompts at minimum, and MUST identify which
  panels received direct user prompt input.
- **FR-033**: The MVP MUST implement only `MockImageProvider` as the active
  image provider for generation.
- **FR-034**: `MockImageProvider` MUST generate deterministic placeholder panel
  images that visibly show the panel index, a short caption or equivalent panel
  label, and whether the request used text-only or reference-image input.
- **FR-035**: The MVP MUST define the boundary for future real text-to-image and
  image-to-image providers without requiring live provider integration, API key
  handling, or provider selection in this feature.
- **FR-036**: The system MUST store all output artifacts under the selected
  output directory.
- **FR-037**: The system MUST provide a single end-to-end command that executes
  one comic generation request at a time.
- **FR-038**: The system MUST create the output directory if it does not exist.
- **FR-039**: The system MUST return a clear error when required input is
  missing.
- **FR-040**: The system MUST return a clear error when a provided reference
  image cannot be read.
- **FR-041**: The system MUST retry a failed image generation step no more than
  two times before marking that step as failed.
- **FR-042**: The MVP MUST run without requiring external image-provider
  credentials.
- **FR-043**: The project MUST include a `README.md` that explains what the
  four-panel comic agent does, how to install or prepare the project, how to
  run the CLI, required and optional CLI arguments, example commands, expected
  output files, high-level project design and module responsibilities, the MVP
  provider boundary, reference-image handling, and how to run tests.
- **FR-044**: `README.md` is a documentation deliverable and part of the
  product contract, but it MUST NOT be treated as a runtime feature or change
  the runtime behavior of the MVP itself.

### Key Entities *(include if feature involves data)*

- **Comic Request**: The full user submission, including the required theme or
  story idea and any optional visual, prompt, language, reference-image, and
  output-location inputs.
- **Character Bible**: The normalized shared character definition derived from
  request inputs and used to keep identity, appearance, and recurring traits
  consistent across all four panels.
- **Story Structure**: The four-panel narrative plan that defines panel order,
  captions, dialogue, scene progression, and pacing for the comic.
- **Style Bible**: The normalized shared style definition derived from request
  inputs and used to keep visual style, atmosphere, and recurring presentation
  details consistent across all four panels.
- **Panel Specification**: The complete content for one panel, including index,
  caption, dialogue, scene description, action, emotion, framing, visual
  description, final prompt, and the path to its 512x512 PNG image.
- **Prompt Guidance Record**: The normalized record of shared prompt guidance,
  per-panel prompt guidance, prompt-merge results, global reference-image
  usage, and any prompt rewrites or safety adjustments.
- **Metadata Record**: The exported run summary containing normalized request
  fields, story output, panel outputs, prompt-source tracking, warnings,
  provider identity, retry counts, and artifact paths.
- **Mock Provider Output**: The deterministic placeholder image content produced
  for a panel by the mock provider, including visible panel identity and input
  mode markers for testing and demonstration.
- **Comic Artifact Set**: The generated panel image files, the final composed
  1054x1054 comic image, and the metadata file for a single request.
- **Documentation Deliverable**: The `README.md` file that describes user-facing
  setup, CLI behavior, outputs, architecture, MVP boundaries, and test usage
  for contributors and operators.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: The system must evaluate user input before image generation,
  reject unsafe theme input before story generation, reject or minimally rewrite
  unsafe or conflicting prompt guidance, and record each rejection or rewrite in
  metadata. Reference images are limited to file validation in this MVP.
- **Out of Scope**: Web interfaces, background processing, multi-request
  scheduling, persistent storage beyond output files, external account
  management, and dependence on live third-party image-generation services are out of scope
  for this MVP.
- **Documentation Scope**: `README.md` is required project documentation for
  this MVP, but it is not itself a runtime feature and does not expand runtime
  scope beyond the clarified CLI behavior.
- **Verification Plan**: The feature is ready for implementation when it can be
  verified through a sample end-to-end generation run, image-size and layout
  checks for the fixed 2x2 canvas, and focused automated checks covering prompt
  construction, metadata recording, reference-image validation, and generation
  behavior without external service credentials.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a standard demonstration run, a user can provide a story idea
  and receive all expected output artifacts in a single execution flow without
  any manual post-processing.
- **SC-002**: 100% of successful runs produce exactly four panel records, four
  panel images, one final comic image, and one metadata file.
- **SC-003**: 100% of successful runs produce four 512x512 panel PNG files and
  one 1054x1054 final comic PNG with the fixed panel order and border layout.
- **SC-004**: In validation runs that include global or per-panel prompt
  guidance, the metadata shows the source of prompt content for every panel.
- **SC-005**: In validation runs with conflicting or unsafe prompt input, every
  rewrite or rejection is visible to the user through an error message or
  metadata entry.
- **SC-006**: In validation runs with unsafe theme input, generation stops
  before story creation and returns a clear rejection outcome.
- **SC-007**: In validation runs with a reference image, the metadata preserves
  the reference-image path, provider identity, and retry information.
- **SC-008**: The MVP can be evaluated in a local environment without requiring
  external image-service credentials.
- **SC-009**: A new contributor can follow `README.md` to install or prepare the
  project, run the CLI with an example command, understand the expected output
  files, and locate the test command set without needing additional setup notes.

## Assumptions

- The primary user is a single creator running the tool locally for one comic
  request at a time.
- The default output language is Chinese when the user does not provide a
  language override.
- The system may use placeholder image generation for MVP validation as long as
  the generated artifacts preserve file structure and metadata behavior.
- The reference image input is optional and applies to image-guided workflows
  rather than being required for every request.
- Per-panel reference images are deferred from this MVP unless a later feature
  explicitly expands the input contract.
- The first CLI release exposes a single command rather than subcommands or
  multiple provider-specific entrypoints.
- `README.md` changes are required when user-facing CLI usage, setup steps,
  output artifacts, project structure expectations, provider behavior, or test
  commands change.
