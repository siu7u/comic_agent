# Planner Selection Contract: LM-assisted story planner

## Purpose

Define the contract for selecting, validating, and tracing LM-assisted story
planning while preserving the existing downstream story-planning contract.

## CLI Selection Contract

- The CLI exposes an explicit per-run planner-selection flag
- The default planner mode may be environment-controlled
- The CLI flag overrides the default planner mode when the user selects it explicitly

## Configuration Contract

- Any LM credentials or endpoint settings required for manual runs are read from
  environment variables
- Planner selection and LM configuration are separate concerns
- The planner-selection flag must not carry secret or endpoint details

## LM Output Contract

- The LM returns one strict JSON object
- The JSON object must be validated before any downstream use
- The validated result must already represent exactly four storyboard panels and be convertible into the current four-panel
  `StoryStructure`

## Validation Contract

The system rejects or ignores LM output when any of the following are true:

- the payload is not valid strict JSON
- the payload does not contain exactly four panels
- required panel fields are missing or empty
- panel content includes page-level layout, collage, split-screen, montage, or
  full comic page instructions
- the payload conflicts with an explicit `request.character` value

## Fallback Contract

- Invalid, unavailable, timed-out, or rejected LM planning results trigger
  automatic fallback to the existing rule-based planner
- Fallback must still produce a valid four-panel `StoryStructure`
- Fallback must not require user intervention during the run

## Metadata Contract

Run-level traceability must record:

- requested planner mode
- actual planner mode used
- whether fallback occurred
- the fallback reason when applicable

## Compatibility Contract

- Prompt generation receives the same final `StoryStructure` contract regardless
  of whether planning came from LM-assisted or rule-based logic
- Provider behavior remains unchanged
- The final `1054x1054` comic image and `10px` `田`-shaped grid border remain
  unchanged

## Verification Contract

Automated verification must include:

- valid LM-assisted planning path coverage
- malformed LM payload coverage
- planner unavailability or timeout fallback coverage
- explicit-character conflict coverage
- metadata traceability coverage
- mock-safe pipeline compatibility coverage

Automated verification must not require:

- live model access
- network access
- external agent frameworks
