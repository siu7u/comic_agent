# Storyboard Expansion Contract

## Purpose

Define the contract for expanding a simple comic theme into a deterministic,
four-panel storyboard while preserving the current pipeline-facing story shape.

## Planning Entrypoints

- Primary planner entrypoint: `plan(request) -> StoryStructure` or equivalent
- Compatibility wrapper: `build_story_structure(request) -> StoryStructure`

## Input Contract

The StoryboardAgent consumes the same request information already available to
the CLI pipeline:

- theme text
- optional explicit character
- optional style and prompt context only as passive downstream context
- existing language and output settings only as passive context

The StoryboardAgent must not require:

- new CLI flags
- network access
- provider configuration
- live model calls

## Semantic Input Contract

The StoryboardAgent must be able to expand a request from one normalized
semantic description containing:

- `subject`
- `activity`
- `primary_object`
- `setting_hint`
- `temporal_cues`
- `domain_cues`

The semantic shape must be the same whether it comes from rule-based parsing or
the LM-assisted semantic parser.

## Subject Resolution Contract

- If an explicit character is provided, that value wins
- Otherwise the agent infers the subject from the theme
- Subject resolution prefers specific phrases over generic ones
- Subject resolution avoids action-heavy phrases when a shorter stable subject
  is available
- If no better subject is available, the agent returns `main character`

## Story Type Detection Contract

The StoryboardAgent selects exactly one story type per request:

- `day_in_the_life`
- `seasonal_progression`
- `journey_adventure`
- `problem_solving`
- `fallback_story`

If multiple structure signals are present, the planner applies a stable
documented priority order and returns one deterministic result.

## Output Contract

The StoryboardAgent returns a `StoryStructure` with exactly four panels.

Each returned panel must include:

- `index`
- `caption`
- `dialogue`
- `scene_description`
- `action`
- `emotion`
- `camera_framing`
- `visual_description`

## Structure-Specific Caption Contract

- Day-in-the-life: `Morning`, `On the Way`, `At School`, `Going Home`
- Seasonal progression: `Spring`, `Summer`, `Autumn`, `Winter`
- Journey or adventure: `Departure`, `Encounter`, `Turning Point`, `Resolution`
- Problem solving: `Problem`, `Search`, `Solution`, `Payoff`
- Fallback story: `Setup`, `Complication`, `Response`, `Resolution`

## Scene Quality Contract

- Each panel describes one concrete visual moment
- Each panel scene is distinct from the other three panels
- No panel asks for multiple seasons, multiple stages, or a full comic page in
  one image
- No panel includes page-level layout instructions
- No panel requests a collage, split-screen, grid, montage, or embedded comic
  page

## Compatibility Contract

- Downstream prompt generation continues to receive a valid four-panel story
  structure
- Character bible and style bible generation continue to consume the same story
  fields
- Metadata export continues to serialize the same story fields
- Provider behavior and final `1054x1054` layout behavior remain unchanged

## Verification Contract

Automated verification must include:

- story type detection coverage
- semantic parsing coverage
- subject extraction coverage
- day-in-the-life expansion coverage
- seasonal progression expansion coverage
- journey or adventure expansion coverage
- problem-solving expansion coverage
- fallback expansion coverage
- compatibility coverage for `build_story_structure(request)`

Automated verification must not require:

- network access
- real provider credentials
- paid API usage
- external agent frameworks
