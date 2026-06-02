# Feature Specification: StoryPlannerAgent refactor

**Feature Branch**: `[003-story-planner-agent]`  
**Created**: 2026-05-29  
**Status**: Draft  
**Input**: User description: "Create a feature specification for refactoring the current story planner into a lightweight agent-oriented StoryPlannerAgent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plan Stronger Visual Stories (Priority: P1)

As a user generating a comic from the CLI, I want the story planner to turn a
theme into four concrete visual scenes so that the resulting four images read as
a coherent visual story instead of four weak variations of the same idea.

**Why this priority**: Story planning quality directly affects every generated
comic, including both mock verification and real-provider runs.

**Independent Test**: Run story planning for a supported theme and verify that
the planner returns exactly four panels with distinct captions, scene
descriptions, visual descriptions, actions, emotions, framing, and dialogue.

**Acceptance Scenarios**:

1. **Given** the theme `一只小兔子上学的一天`, **When** the planner builds the
   story structure, **Then** it returns exactly four panels with captions
   `Morning`, `On the Way`, `At School`, and `Going Home`.
2. **Given** the theme `一只小兔子上学的一天`, **When** the planner builds the
   story structure, **Then** the four panels describe concrete scenes covering
   home departure, the journey to school, school activity, and end-of-day
   return or resolution.

---

### User Story 2 - Detect Common Story Intents (Priority: P2)

As a contributor, I want story planning to detect common intent types such as
seasonal progression, school-day sequences, competition climaxes, and growth
journeys so that similar themes consistently produce concrete, appropriate
four-panel story beats.

**Why this priority**: Intent detection is the smallest planning improvement
that raises quality across multiple theme categories without introducing an
external planning system.

**Independent Test**: Run planning for one theme from each supported intent
category and verify that the returned captions and scene progression match the
expected planning pattern for that intent.

**Acceptance Scenarios**:

1. **Given** the theme `记录同一只流浪橘猫在四季中的变化，特征保持一致`,
   **When** the planner builds the story structure, **Then** it returns exactly
   four panels with captions `Spring`, `Summer`, `Autumn`, and `Winter`.
2. **Given** a seasonal theme, **When** the planner builds the story
   structure, **Then** each panel describes one season only and no panel asks
   for all seasons in a single image.
3. **Given** a journey, transformation, or growth theme, **When** the planner
   builds the story structure, **Then** the four panels represent distinct
   stages of progression with concrete scene descriptions.
4. **Given** the theme `狐狸参加篮球赛，投进绝杀三分`, **When** the planner
   builds the story structure, **Then** it returns exactly four panels with
   concrete competition scenes covering the opening, pressure, decisive action,
   and finish of the match.

---

### User Story 3 - Preserve Pipeline Compatibility (Priority: P3)

As a contributor maintaining the comic pipeline, I want the planner refactor to
preserve the existing output contract and deterministic behavior so that the new
planning quality does not break prompt generation, provider execution, layout,
or metadata export.

**Why this priority**: The planning refactor is valuable only if it improves
story quality without destabilizing the rest of the pipeline.

**Independent Test**: Run existing compatibility-safe pipeline tests and verify
that the planner still returns a valid four-panel `StoryStructure` consumable by
the rest of the pipeline without requiring network access or real provider
credentials.

**Acceptance Scenarios**:

1. **Given** existing pipeline code that calls `build_story_structure(request)`,
   **When** the refactor is introduced, **Then** the call still returns a valid
   four-panel story structure compatible with current prompt building and
   metadata export.
2. **Given** automated tests running without network access or provider
   credentials, **When** planner tests and existing mock-safe pipeline tests
   run, **Then** they complete without live provider calls.

### Edge Cases

- What happens when the theme contains more than one detectable intent pattern,
  such as both a school-day and a growth keyword?
- How does the planner behave when a theme implies progression but does not name
  a clear subject?
- What happens when the user supplies `--character` and it conflicts with the
  subject inferred from the theme?
- How does the planner handle themes that are safe but abstract, so fallback
  planning must still produce four distinct concrete scenes?
- What happens when a seasonal theme includes all-season wording that could
  accidentally encourage one panel to show multiple seasons?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a lightweight internal planning component
  named `StoryPlannerAgent` or an equivalent agent-like planner with one clear
  planning entrypoint for comic story generation.
- **FR-002**: The planner MUST normalize the incoming request before creating
  panel story beats.
- **FR-003**: The planner MUST determine the main subject from
  `request.character` when that field is provided.
- **FR-004**: The planner MUST infer the main subject from the theme when
  `request.character` is absent and MUST fall back to `main character` only
  when no better subject can be detected.
- **FR-005**: Subject extraction MUST prefer more specific subject phrases over
  generic ones, including patterns such as `流浪橘猫` before `橘猫` before `猫`,
  `小兔子` before `小兔` before `兔子`, `小狐狸` before `狐狸` before `狐`,
  `小狗` before `狗`, and `小猫` before `猫`.
- **FR-006**: Subject extraction MUST avoid returning long action phrases such
  as `小兔子上学` when the intended subject is only `小兔子`.
- **FR-007**: The planner MUST detect four-season or seasonal progression
  intent for themes containing `四季`, `春夏秋冬`, or `spring, summer, autumn,
  winter`.
- **FR-008**: For seasonal progression intent, the planner MUST produce exactly
  four panels with captions `Spring`, `Summer`, `Autumn`, and `Winter`.
- **FR-009**: For seasonal progression intent, each panel MUST describe one
  season only and MUST NOT describe all seasons in one image.
- **FR-010**: The planner MUST detect school-day or day-in-the-life intent for
  themes containing terms such as `上学`, `学校`, `一天`, `放学`, `school`, or
  `day in the life`.
- **FR-011**: For school-day intent, the planner MUST produce exactly four
  panels with captions `Morning`, `On the Way`, `At School`, and `Going Home`.
- **FR-012**: For school-day intent, the planner MUST produce concrete scenes
  covering departure from home, the trip to school, a school or classroom
  activity, and return home or an end-of-day resolution.
- **FR-013**: The planner MUST detect journey, transformation, or growth intent
  for themes containing terms such as `旅程`, `变化`, `成长`, `progression`,
  `transformation`, `journey`, or `growth`.
- **FR-014**: For journey, transformation, or growth intent, the planner MUST
  produce exactly four panels with captions `Beginning`, `Challenge`, `Change`,
  and `Result`.
- **FR-015**: The planner MUST detect competition-climax intent for themes
  containing terms such as `比赛`, `球赛`, `篮球赛`, `足球赛`, `决赛`, `绝杀`,
  `冠军`, `夺冠`, `game`, `match`, `tournament`, `final`, `championship`, or
  `buzzer-beater`.
- **FR-016**: For competition-climax intent, the planner MUST produce exactly
  four panels with captions `Opening`, `Pressure`, `Climax`, and `Finish`.
- **FR-017**: For competition-climax intent, the planner MUST produce concrete
  scenes covering pre-match setup, in-game pressure, the decisive play, and the
  immediate visible outcome.
- **FR-018**: When no supported intent is detected, the planner MUST use a
  fallback gag-comic structure with captions `Setup`, `Complication`,
  `Response`, and `Resolution`.
- **FR-019**: The planner MUST always return exactly four panels.
- **FR-020**: Each returned panel MUST have a distinct caption.
- **FR-021**: Each returned panel MUST have a distinct and concrete
  `scene_description`.
- **FR-022**: Each returned panel MUST have a `visual_description` that does
  not simply repeat the full theme text.
- **FR-023**: Each returned panel MUST have an `action` that describes a
  concrete panel-level action.
- **FR-024**: Each returned panel MUST include `emotion`, `camera_framing`,
  `caption`, and `dialogue` fields suitable for downstream prompt generation.
- **FR-025**: The planner MUST NOT generate page-level layout instructions.
- **FR-026**: The planner MUST NOT ask any panel to contain multiple panels, a
  collage, or a full comic page.
- **FR-027**: The refactor MUST preserve the existing `StoryStructure` and
  `PanelSpec` output contract unless a small additive field is required for
  planning traceability.
- **FR-028**: `build_story_structure(request)` MAY remain as a compatibility
  wrapper, but it MUST delegate to the new planner behavior.
- **FR-029**: The refactor MUST preserve existing CLI behavior.
- **FR-030**: The refactor MUST preserve existing provider behavior for both
  mock and real image providers.
- **FR-031**: The refactor MUST preserve the existing final image layout,
  including the `1054x1054` final comic image and `10px` `田`-shaped grid
  border.
- **FR-032**: The planner MUST remain deterministic and testable without
  external model calls.
- **FR-033**: Automated tests for the planner and pipeline compatibility MUST
  run without network access or real provider credentials.
- **FR-034**: The system MUST define explicit verification coverage for intent
  detection, subject extraction, seasonal planning, school-day planning,
  competition-climax planning, journey planning, fallback planning, and
  compatibility delegation.
- **FR-035**: README.md MUST be updated if contributor-facing architecture
  description or workflow expectations change because of this refactor.

### Key Entities *(include if feature involves data)*

- **StoryPlannerAgent**: The internal planning component responsible for
  normalizing a request, extracting the subject, detecting intent, and
  producing a four-panel story structure.
- **Story Intent Type**: The planning category inferred from the request, such
  as seasonal progression, school-day, competition climax, journey or growth
  progression, or fallback gag-comic.
- **Planning Context**: The normalized planning input composed of request theme,
  optional explicit character, inferred subject, and detected intent.
- **Planned Panel Beat**: One of the exactly four returned panel definitions,
  including caption, dialogue, scene description, visual description, action,
  emotion, and camera framing.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: The refactor must preserve the current pipeline rule that
  unsafe themes are rejected before image generation. Planner output must remain
  limited to one visual scene per panel and must not introduce page-level or
  multi-panel instructions that conflict with downstream single-scene prompt
  generation.
- **Out of Scope**: Adding new image providers, modifying `WanxImageProvider`,
  real image-to-image generation, per-panel reference images, changing the
  final image layout, changing CLI arguments, introducing external agent
  frameworks, using live model calls for story planning, web UI, database,
  queueing, and background jobs.
- **Verification Plan**: After implementation, run the smallest relevant
  planner-focused unit tests plus the existing mock-safe pipeline compatibility
  test command, and avoid any required live provider call in automated
  verification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For the theme `一只小兔子上学的一天`, the planner returns exactly
  four panels with captions `Morning`, `On the Way`, `At School`, and
  `Going Home`, and each panel describes a different concrete scene.
- **SC-002**: For the theme `记录同一只流浪橘猫在四季中的变化，特征保持一致`,
  the planner returns exactly four panels with captions `Spring`, `Summer`,
  `Autumn`, and `Winter`, and each panel describes only one season.
- **SC-003**: For a generic fallback theme, all four panel scene descriptions
  are distinct from one another and are not identical copies of the theme text.
- **SC-004**: For the theme `狐狸参加篮球赛，投进绝杀三分`, the planner
  returns exactly four panels with captions `Opening`, `Pressure`, `Climax`,
  and `Finish`, and the third panel describes the decisive scoring attempt as a
  single concrete scene.
- **SC-005**: Existing mock-safe pipeline verification continues to pass after
  the refactor without requiring network access or real provider credentials.
- **SC-006**: The refactor introduces no external agent framework and no live
  planning call dependency.

## Assumptions

- The project will continue to use deterministic local planning logic rather
  than external model-based planning.
- The existing prompt-building, provider, composition, and metadata stages will
  continue to consume a four-panel `StoryStructure`.
- The refactor may improve internal organization and naming, but contributor
  value comes from better panel scene quality rather than from new CLI surface
  area.
- When a theme matches multiple intent signals, the planner can apply a stable
  deterministic priority order as long as the chosen behavior is documented and
  tested.
