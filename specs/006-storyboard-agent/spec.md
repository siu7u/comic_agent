# Feature Specification: StoryboardAgent for Four-Panel Story Expansion

**Feature Branch**: `006-storyboard-agent`  
**Created**: 2026-05-29  
**Status**: Draft  
**Input**: User description: "Create a feature specification for a StoryboardAgent that expands a simple user prompt into a structured four-panel story."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expand Simple Daily Stories (Priority: P1)

As a comic creator, I want a short daily-life prompt to expand into four concrete panel scenes so that the resulting comic reads like a clear visual story instead of four generic variations of the same idea.

**Why this priority**: Day-in-the-life prompts are a common and representative input pattern, and they expose the current weakness most clearly when scenes repeat or stay abstract.

**Independent Test**: Can be fully tested by submitting a simple day-in-the-life prompt and verifying that the returned four panels form a complete, distinct progression with concrete visual scenes.

**Acceptance Scenarios**:

1. **Given** a request with the theme `一只小兔子上学的一天`, **When** the StoryboardAgent expands it, **Then** it returns exactly four panels with captions `Morning`, `On the Way`, `At School`, and `Going Home`.
2. **Given** a request with the theme `一只小兔子上学的一天`, **When** the StoryboardAgent expands it, **Then** each panel contains a concrete and distinct scene description covering departure, travel, school activity, and return home.

---

### User Story 2 - Expand Recognized Story Structures (Priority: P2)

As a comic creator, I want the system to recognize common story patterns such as seasons, journeys, and problem solving so that short prompts become structured four-panel stories with appropriate progression.

**Why this priority**: Recognized structures provide the biggest quality improvement after daily-life stories because they let the system turn compact prompts into visually distinct stages instead of generic fallback beats.

**Independent Test**: Can be fully tested by submitting one prompt for each recognized structure type and verifying that the panel captions, scenes, and stage progression match the expected structure.

**Acceptance Scenarios**:

1. **Given** a request with the theme `记录同一只流浪橘猫在四季中的变化，特征保持一致`, **When** the StoryboardAgent expands it, **Then** it returns four panels with captions `Spring`, `Summer`, `Autumn`, and `Winter`, and each panel describes only one season.
2. **Given** a request with the theme `一只狐狸放飞灯笼`, **When** the StoryboardAgent expands it, **Then** it returns four panels that progress from preparation to encounter or launch, to turning point, to resolution with concrete scene descriptions.
3. **Given** a request with the theme `机器人修好城市的灯`, **When** the StoryboardAgent expands it, **Then** it returns four panels with a clear problem, search, solution, and payoff progression.

---

### User Story 3 - Preserve Pipeline Compatibility (Priority: P3)

As a maintainer, I want storyboard expansion to remain compatible with the current comic pipeline so that prompt generation, providers, final layout, and metadata export continue to work without external services or interface breaks.

**Why this priority**: The feature only delivers value if it improves story quality without destabilizing the existing CLI workflow and downstream image-generation pipeline.

**Independent Test**: Can be fully tested by using the compatibility wrapper and existing mock-safe pipeline coverage to confirm that the output still matches the current story structure contract and can flow into downstream prompt generation.

**Acceptance Scenarios**:

1. **Given** an existing pipeline call path that uses the story-building entrypoint, **When** the StoryboardAgent is introduced behind that entrypoint, **Then** the returned object remains compatible with the current `StoryStructure` and `PanelSpec` contract.
2. **Given** a mock-provider pipeline run, **When** storyboard expansion is used, **Then** the pipeline still completes without external network calls and produces the expected metadata and final comic artifacts.

### Edge Cases

- What happens when the theme is too vague to match a recognized story type, such as a short noun phrase or a whimsical prompt with no clear progression?
- What happens when the theme mixes multiple possible structures, such as day-in-the-life plus seasonal progression?
- What happens when the user provides `--character` that conflicts with the theme subject?
- What happens when no subject can be inferred from the theme?
- What happens when a request is unsafe and must be rejected before any downstream generation steps run?
- How does the system preserve a valid four-panel output when the story must fall back to the generic structure?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a lightweight internal StoryboardAgent or equivalent component responsible for expanding a simple comic theme into a structured four-panel story.
- **FR-002**: The StoryboardAgent MUST accept the existing `ComicRequest` as input and return output compatible with the existing `StoryStructure` and `PanelSpec` contract.
- **FR-003**: The StoryboardAgent MUST provide one clear planning entrypoint, such as `expand(request)` or `plan(request)`.
- **FR-004**: The existing `build_story_structure(request)` entrypoint MAY remain as a compatibility wrapper, but it MUST delegate storyboard expansion to the StoryboardAgent.
- **FR-005**: The StoryboardAgent MUST always generate exactly four panels.
- **FR-006**: Each generated panel MUST include `index`, `caption`, `dialogue`, `scene_description`, `action`, `emotion`, `camera_framing`, and `visual_description`.
- **FR-007**: Each panel `scene_description` MUST be concrete, visual, image-friendly, and distinct from the other panel scene descriptions in the same story.
- **FR-008**: The StoryboardAgent MUST avoid repeating the full user theme as every panel `scene_description` or `visual_description`.
- **FR-009**: Each panel MUST describe exactly one scene and one stage of progression only.
- **FR-010**: The StoryboardAgent MUST NOT include page-level layout instructions such as `four-panel layout`, `grid`, `comic page`, or equivalent layout directions inside panel story descriptions.
- **FR-011**: The StoryboardAgent MUST support, at minimum, day-in-the-life stories, seasonal or time progression stories, journey or adventure stories, problem-solving stories, and a generic fallback story structure.
- **FR-012**: For day-in-the-life stories, the StoryboardAgent MUST produce the four-stage progression `Morning`, `On the Way`, `At School`, `Going Home`, or equivalent basic bilingual variants when appropriate.
- **FR-013**: For seasonal or time progression stories, the StoryboardAgent MUST produce one panel per seasonal or time stage and MUST NOT ask any panel to show multiple seasons or stages in one image.
- **FR-014**: For journey or adventure stories, the StoryboardAgent MUST produce the progression `Departure`, `Encounter`, `Turning Point`, and `Resolution`, or equivalent basic bilingual variants when appropriate.
- **FR-015**: For problem-solving stories, the StoryboardAgent MUST produce the progression `Problem`, `Search`, `Solution`, and `Payoff`, or equivalent basic bilingual variants when appropriate.
- **FR-016**: For prompts that do not match a recognized structure, the StoryboardAgent MUST fall back to `Setup`, `Complication`, `Response`, and `Resolution` while still producing distinct and concrete scenes.
- **FR-017**: If the request includes a character override, the StoryboardAgent MUST use that value as the main subject.
- **FR-018**: If no character override is provided, the StoryboardAgent MUST infer the main subject from the theme when possible.
- **FR-019**: Subject extraction MUST prefer more specific subject keywords over more generic keywords and MUST avoid returning action phrases such as `小兔子上学` or `狐狸放飞灯笼`.
- **FR-020**: If no subject can be inferred, the StoryboardAgent MUST fall back to `main character`.
- **FR-021**: The StoryboardAgent MUST support Chinese and English prompts at a basic keyword-driven level sufficient to detect the supported story types and infer a subject when possible.
- **FR-022**: The default StoryboardAgent path MUST remain deterministic and testable without external model calls, external image providers, provider credentials, or network access.
- **FR-022a**: When LM-assisted planning is enabled elsewhere in the pipeline, the StoryboardAgent MUST be able to consume one structured semantic result so both planning modes share the same downstream storyboard expansion path.
- **FR-023**: The StoryboardAgent MUST preserve existing CLI behavior, provider behavior, final layout behavior, and metadata export compatibility.
- **FR-024**: The system MUST define explicit output artifacts for this feature as the existing story structure passed into the current prompt-generation and export pipeline, with no new required external artifacts.
- **FR-025**: The system MUST specify that automated verification for this feature uses mock-safe tests and does not require live image-provider calls.
- **FR-026**: The storyboard output MUST remain suitable for downstream character consistency, style consistency, and safety filtering already present in the pipeline.
- **FR-027**: README.md MUST be updated if the new StoryboardAgent changes the documented architecture or contributor workflow.

### Key Entities *(include if feature involves data)*

- **StoryboardAgent**: The internal component that interprets a `ComicRequest`, identifies a story type, determines the subject, and expands the input into a four-panel story.
- **StoryStructure**: The four-panel story output consumed by downstream prompt generation and metadata export, including story title, premise, subject, and ordered panels.
- **Panel Story Beat**: One panel-level story moment containing caption, dialogue, scene description, action, emotion, camera framing, and visual description for exactly one image scene.
- **Story Type**: The detected structural category used to expand the prompt, such as day-in-the-life, seasonal progression, journey or adventure, problem solving, or fallback.
- **Subject**: The primary character or focal entity that remains visually and narratively central across the four-panel story.

## Safety and Scope Constraints *(mandatory)*

- **Safety Rules**: Unsafe themes MUST continue to be rejected before any downstream generation side effects occur; storyboard expansion MUST not bypass existing safety gates or introduce scene descriptions that widen unsafe content beyond the original request.
- **Out of Scope**: Adding new image providers, modifying WanxImageProvider, changing final layout behavior, changing CLI arguments, introducing external LLM calls, adding external agent frameworks, real image-to-image generation, per-panel reference images, web UI, databases, and background job systems.
- **Verification Plan**: Verify with mock-safe story expansion and pipeline compatibility checks that cover recognized story types, subject extraction, fallback behavior, and compile-time validation without requiring live provider calls.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each supported story type, 100% of tested inputs produce exactly four panels with distinct captions and stage-appropriate progression.
- **SC-002**: For the regression inputs `一只小兔子上学的一天`, `记录同一只流浪橘猫在四季中的变化，特征保持一致`, and `一只狐狸放飞灯笼`, all four panels contain concrete and visually distinct scene descriptions instead of repeated generic placeholders.
- **SC-003**: 100% of automated tests for this feature run without network access, provider credentials, or paid API usage.
- **SC-004**: Existing prompt-builder and mock-provider compatibility tests continue to pass after the StoryboardAgent is introduced.
- **SC-005**: For recognized seasonal prompts, 0 panels in the regression suite ask for multiple seasons in the same image.
- **SC-006**: For recognized day-in-the-life prompts, 100% of regression panels cover departure, transit, destination activity, and return or end-of-day closure in order.

## Assumptions

- The current comic pipeline already has a stable downstream contract for story structures, panel prompts, providers, layout, and metadata export, and this feature will build on that contract rather than replace it.
- The default local storyboard expansion path remains available without any LM dependency.
- Basic bilingual support means the agent can recognize and expand common Chinese and English prompt patterns without needing full natural-language understanding.
- The current safety checks remain the authoritative guardrail for unsafe themes and are executed before storyboard expansion causes downstream side effects.
- The feature improves story quality at the planning layer only and does not guarantee image-provider compliance with every visual instruction.
