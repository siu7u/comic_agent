# Story Planning Contract: StoryPlannerAgent refactor

## Purpose

Define the planning contract for the internal story planner while preserving the
existing pipeline-facing story structure contract.

## Planning Entrypoints

- Primary planner entrypoint: `plan(request) -> StoryStructure`
- Compatibility wrapper: `build_story_structure(request) -> StoryStructure`

## Input Contract

The planner consumes the same request information already available to the CLI
pipeline:

- theme text
- optional explicit character
- optional reference-image presence flag
- existing language and output settings only as passive context

The planner must not require:

- new CLI flags
- live model calls
- network access
- provider configuration

## Subject Resolution Contract

- If an explicit character is provided, that value wins
- Otherwise the planner infers the subject from the theme
- Subject resolution must prefer specific phrases over generic ones
- Subject resolution must avoid returning action-heavy phrases when a shorter
  stable subject is available
- If no better subject is available, the planner returns `main character`

## Intent Detection Contract

The planner selects exactly one intent type per request:

- `seasonal_progression`
- `school_day`
- `competition_climax`
- `journey_growth`
- `fallback_gag`

If multiple intent signals are present, the planner applies a stable documented
priority order and returns one deterministic result.

## Output Contract

The planner returns a `StoryStructure` with exactly four panels.

Each returned panel must include:

- `caption`
- `dialogue`
- `scene_description`
- `visual_description`
- `action`
- `emotion`
- `camera_framing`

## Intent-Specific Caption Contract

- Seasonal progression: `Spring`, `Summer`, `Autumn`, `Winter`
- School-day: `Morning`, `On the Way`, `At School`, `Going Home`
- Competition climax: `Opening`, `Pressure`, `Climax`, `Finish`
- Journey or growth: `Beginning`, `Challenge`, `Change`, `Result`
- Fallback gag-comic: `Setup`, `Complication`, `Response`, `Resolution`

## Scene Quality Contract

- Each panel describes one concrete visual moment
- Each panel scene is distinct from the other three panels
- No panel asks for all seasons, all stages, or a whole comic page in one image
- No panel includes page-level layout instructions
- No panel requests a collage, split-screen, grid, montage, or embedded comic
  page

## Compatibility Contract

- Downstream prompt generation continues to receive a valid four-panel story
  structure
- Metadata export continues to serialize the same story fields
- Provider behavior and final 2x2 layout behavior remain unchanged

## Verification Contract

Automated verification must include:

- intent detection coverage
- subject extraction coverage
- seasonal planning coverage
- school-day planning coverage
- competition-climax planning coverage
- journey or growth planning coverage
- fallback planning coverage
- compatibility coverage for `build_story_structure(request)`

Automated verification must not require:

- network access
- real provider credentials
- external agent frameworks
