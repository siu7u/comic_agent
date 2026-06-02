from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from comic_agent.models.comic_request import ComicRequest
from comic_agent.models.metadata import PlannerRunRecord
from comic_agent.models.panel import PanelSpec, StoryStructure


RULE_BASED_PLANNER_MODE = "rule_based"
LM_ASSISTED_PLANNER_MODE = "lm_assisted"
SUPPORTED_PLANNER_MODES = (RULE_BASED_PLANNER_MODE, LM_ASSISTED_PLANNER_MODE)

COMIC_AGENT_LM_API_URL_ENV = os.getenv("COMIC_AGENT_LM_API_URL_ENV", "COMIC_AGENT_LM_API_URL").strip()
COMIC_AGENT_LM_API_KEY_ENV = os.getenv("COMIC_AGENT_LM_API_KEY_ENV", "COMIC_AGENT_LM_API_KEY").strip()
COMIC_AGENT_LM_MODEL_ENV = os.getenv("COMIC_AGENT_LM_MODEL_ENV", "COMIC_AGENT_LM_MODEL").strip()
COMIC_AGENT_LM_TIMEOUT_ENV = os.getenv("COMIC_AGENT_LM_TIMEOUT_ENV", "COMIC_AGENT_LM_TIMEOUT").strip()
COMIC_AGENT_LM_ENABLED_ENV = os.getenv("COMIC_AGENT_LM_ENABLED_ENV", "COMIC_AGENT_LM_ENABLED").strip()
DEFAULT_LM_TIMEOUT_SECONDS = 20.0

REJECTED_LAYOUT_TERMS = (
    "collage",
    "split-screen",
    "split screen",
    "grid",
    "internal comic layout",
    "four-panel layout",
    "four panel layout",
    "four-panel comic",
    "four panel comic",
    "comic page",
    "full comic page",
    "montage",
    "seasonal comparison layout",
)
LM_REQUIRED_PANEL_FIELDS = (
    "caption",
    "dialogue",
    "scene_description",
    "action",
    "emotion",
    "camera_framing",
    "visual_description",
)
LM_REQUIRED_STORYBOARD_FIELDS = (
    "subject",
    "panels",
)


@dataclass(slots=True)
class PlanningContext:
    raw_theme: str
    normalized_theme: str
    explicit_character: str | None
    subject: str
    intent_type: str
    semantics: "ThemeSemantics"


@dataclass(frozen=True, slots=True)
class ThemeSemantics:
    subject: str
    activity: str
    primary_object: str
    setting_hint: str
    temporal_cues: tuple[str, ...]
    domain_cues: tuple[str, ...]
    source: str = "rule_based"


@dataclass(frozen=True, slots=True)
class BeatSpec:
    caption: str
    action: str
    emotion: str
    camera_framing: str


@dataclass(frozen=True, slots=True)
class ShotSpec:
    location: str
    subject_pose: str
    primary_action: str
    visible_props: str
    instant_detail: str


@dataclass(frozen=True, slots=True)
class LMConfiguration:
    api_url: str
    api_key: str
    model: str
    timeout_seconds: float


class LMPlanningError(RuntimeError):
    pass


FALLBACK_BEATS = [
    BeatSpec("Setup", "Show the opening situation in one clear scene", "curious", "wide shot"),
    BeatSpec("Complication", "Show the first visible obstacle in one clear scene", "tense", "medium shot"),
    BeatSpec("Response", "Show the main response to the obstacle in one clear scene", "determined", "medium shot"),
    BeatSpec("Resolution", "Show the ending payoff in one clear scene", "joyful", "wide shot"),
]
SEASONAL_BEATS = [
    BeatSpec("Spring", "Show the spring stage of the character's progression", "hopeful", "wide shot"),
    BeatSpec("Summer", "Show the summer stage of the character's progression", "energetic", "medium shot"),
    BeatSpec("Autumn", "Show the autumn stage of the character's progression", "reflective", "medium shot"),
    BeatSpec("Winter", "Show the winter stage of the character's progression", "calm", "wide shot"),
]
DAY_IN_THE_LIFE_BEATS = [
    BeatSpec("Morning", "Leave home and begin the day", "eager", "wide shot"),
    BeatSpec("On the Way", "Travel toward school and react to the journey", "focused", "medium shot"),
    BeatSpec("At School", "Take part in a classroom or school activity", "engaged", "medium shot"),
    BeatSpec("Going Home", "Return home and close the day", "relieved", "wide shot"),
]
JOURNEY_BEATS = [
    BeatSpec("Departure", "Show the beginning of the journey in one clear scene", "hopeful", "wide shot"),
    BeatSpec("Encounter", "Show the first important event or obstacle on the journey", "alert", "medium shot"),
    BeatSpec("Turning Point", "Show the decisive change in the journey", "determined", "close-up"),
    BeatSpec("Resolution", "Show the resolved ending of the journey", "joyful", "wide shot"),
]
PROBLEM_SOLVING_BEATS = [
    BeatSpec("Problem", "Show the visible problem in one clear scene", "concerned", "wide shot"),
    BeatSpec("Search", "Show the investigation or search in one clear scene", "focused", "medium shot"),
    BeatSpec("Solution", "Show the repair or solution attempt in one clear scene", "determined", "close-up"),
    BeatSpec("Payoff", "Show the successful outcome in one clear scene", "relieved", "wide shot"),
]
COMPETITION_BEATS = [
    BeatSpec("Opening", "Establish the competitive setting before the decisive action", "focused", "wide shot"),
    BeatSpec("Pressure", "Show the main on-field or on-court challenge", "tense", "medium shot"),
    BeatSpec("Climax", "Show the decisive attempt in one clear action moment", "determined", "close-up"),
    BeatSpec("Finish", "Show the result and immediate reaction after the decisive moment", "triumphant", "wide shot"),
]

SPECIFIC_SUBJECT_PATTERNS = [
    "流浪橘猫",
    "橘猫",
    "小兔子",
    "小兔",
    "兔子",
    "小狐狸",
    "狐狸",
    "狐",
    "小狗",
    "狗",
    "小猫",
    "猫",
    "机器人",
    "小男孩",
    "小女孩",
]
GENERIC_SUBJECT_PATTERNS = [
    "青蛙",
    "蛙",
    "熊",
    "乌鸦",
    "浣熊",
    "乌龟",
    "鼹鼠",
    "robot",
    "boy",
    "girl",
    "bird",
    "fox",
    "frog",
    "rabbit",
    "cat",
    "dog",
]


def normalize_planner_mode(value: str | None) -> str:
    normalized = (value or default_planner_mode()).strip().lower()
    if normalized not in SUPPORTED_PLANNER_MODES:
        allowed = ", ".join(SUPPORTED_PLANNER_MODES)
        raise ValueError(f"Unsupported planner mode: {value}. Expected one of: {allowed}")
    return normalized


def default_planner_mode() -> str:
    raw_value = os.getenv(COMIC_AGENT_LM_ENABLED_ENV)
    if raw_value is None:
        return LM_ASSISTED_PLANNER_MODE
    normalized = raw_value.strip().lower()
    if normalized in {"0", "false", "no", "off", "disabled", "disable"}:
        return RULE_BASED_PLANNER_MODE
    return LM_ASSISTED_PLANNER_MODE


def plan_story(request: ComicRequest) -> tuple[StoryStructure, PlannerRunRecord]:
    requested_mode = normalize_planner_mode(request.planner_mode)
    request.planner_mode = requested_mode
    if requested_mode == RULE_BASED_PLANNER_MODE:
        story = StoryboardAgent().plan(request)
        return story, PlannerRunRecord(
            requested_mode=RULE_BASED_PLANNER_MODE,
            actual_mode=RULE_BASED_PLANNER_MODE,
        )

    try:
        story = LMStoryPlanner().plan(request)
    except LMPlanningError as exc:
        fallback_story = StoryboardAgent().plan(request)
        return fallback_story, PlannerRunRecord(
            requested_mode=LM_ASSISTED_PLANNER_MODE,
            actual_mode=RULE_BASED_PLANNER_MODE,
            fallback_triggered=True,
            fallback_reason=str(exc),
        )
    return story, PlannerRunRecord(
        requested_mode=LM_ASSISTED_PLANNER_MODE,
        actual_mode=LM_ASSISTED_PLANNER_MODE,
    )


def build_story_structure(request: ComicRequest) -> StoryStructure:
    return plan_story(request)[0]


def resolve_story_subject(request: ComicRequest) -> str:
    return StoryboardAgent().build_context(request).subject


class StoryboardAgent:
    def plan(self, request: ComicRequest) -> StoryStructure:
        context = self.build_context(request)
        return self._story_from_context(context, request)

    def plan_from_semantics(self, request: ComicRequest, semantics: ThemeSemantics) -> StoryStructure:
        context = self.build_context(request, semantics_override=semantics)
        return self._story_from_context(context, request)

    def _story_from_context(self, context: PlanningContext, request: ComicRequest) -> StoryStructure:
        panels = self._build_panels(context, request)
        return StoryStructure(
            title=f"Story sequence: {request.theme}",
            premise=f"A four-step visual story about {request.theme} featuring {context.subject}.",
            panels=panels,
            subject=context.subject,
        )

    def build_context(self, request: ComicRequest, semantics_override: ThemeSemantics | None = None) -> PlanningContext:
        normalized_theme = " ".join(request.theme.strip().split())
        subject = self._resolve_subject(request.character, normalized_theme)
        semantics = semantics_override or self._parse_theme_semantics(normalized_theme, subject)
        subject = request.character.strip() if request.character else semantics.subject or subject
        intent_type = self._detect_intent(normalized_theme, semantics)
        return PlanningContext(
            raw_theme=request.theme,
            normalized_theme=normalized_theme,
            explicit_character=request.character,
            subject=subject,
            intent_type=intent_type,
            semantics=semantics,
        )

    def _build_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        builders = {
            "seasonal_progression": self._build_seasonal_panels,
            "day_in_the_life": self._build_day_in_the_life_panels,
            "journey_adventure": self._build_journey_panels,
            "problem_solving": self._build_problem_solving_panels,
            "competition_climax": self._build_competition_panels,
            "fallback_story": self._build_fallback_panels,
        }
        return builders[context.intent_type](context, request)

    def _build_seasonal_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        scenes = [
            ShotSpec(
                location="a spring alley beside fresh grass and damp stone",
                subject_pose="walks under flowering branches with the body angled forward",
                primary_action="placing one paw or foot onto the rain-dark ground",
                visible_props="blossom petals, wet pavement, and a warm alley wall",
                instant_detail="catch the instant just after light rain when the subject passes beneath the blossoms",
            ),
            ShotSpec(
                location="a summer street edge with deep shade beside a sunlit road",
                subject_pose="rests low in the shade with the head turned toward the bright street",
                primary_action="cooling down while pausing from the heat",
                visible_props="dense leaves, hard sunlight, and warm pavement",
                instant_detail="freeze the instant when the subject settles into the shade away from the strongest sun",
            ),
            ShotSpec(
                location="an autumn lane covered with dry fallen leaves",
                subject_pose="stands mid-step beside a small leaf pile with the tail or body turned into the wind",
                primary_action="pausing as wind lifts the leaves nearby",
                visible_props="fallen leaves, golden trees, and crisp evening air",
                instant_detail="show one exact gust of wind moving the leaves around the subject",
            ),
            ShotSpec(
                location="a sheltered winter corner beside a wall with thin snow nearby",
                subject_pose="curls inward close to the ground to hold warmth",
                primary_action="settling into the protected corner against the cold",
                visible_props="thin snow, bare branches, and cold blue night light",
                instant_detail="freeze the instant when the subject tucks into the corner and the cold air feels visible",
            ),
        ]
        return self._panel_specs_from_beats(context, request, SEASONAL_BEATS, scenes)

    def _build_day_in_the_life_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        scenes = [
            ShotSpec(
                location="the front door of home in clear morning light",
                subject_pose="stands upright at the doorway with the bag straps held close",
                primary_action="taking the first step out to begin school",
                visible_props="a small school bag, the doorway, and a sunlit path ahead",
                instant_detail="freeze the exact instant when the subject leaves home and looks toward the day ahead",
            ),
            ShotSpec(
                location="the road to school with plants and early light along the path",
                subject_pose="leans forward into a steady walking stride",
                primary_action="walking toward school with purpose",
                visible_props="the school road, nearby plants or buildings, and the school bag in motion",
                instant_detail="show one exact stride on the way to school rather than the whole journey",
            ),
            ShotSpec(
                location="a bright classroom with desks and study materials",
                subject_pose="sits at the desk with the upper body angled toward the lesson",
                primary_action="listening and working during class",
                visible_props="books, pencils, desks, and a classroom board",
                instant_detail="freeze the moment of focused attention during one classroom activity",
            ),
            ShotSpec(
                location="the road home in warm evening light",
                subject_pose="walks with a lighter posture and the bag resting against the back",
                primary_action="heading home after the school day ends",
                visible_props="the school bag, evening light, and the familiar road home",
                instant_detail="catch the exact return-home moment with the day ending around the subject",
            ),
        ]
        return self._panel_specs_from_beats(context, request, DAY_IN_THE_LIFE_BEATS, scenes)

    def _build_journey_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        if context.semantics.primary_object in {"灯笼", "lantern"}:
            scenes = [
                ShotSpec(
                    location="a dusk courtyard or open doorway before night falls",
                    subject_pose="leans over the lantern frame with careful hands or paws",
                    primary_action="preparing the paper lantern for release",
                    visible_props="the lantern frame, thin paper, and soft dusk light",
                    instant_detail="freeze the exact instant when the subject finishes a careful adjustment on the lantern",
                ),
                ShotSpec(
                    location="an open outdoor place beneath the first darkening sky",
                    subject_pose="holds the lantern upright close to the body while facing upward space",
                    primary_action="lighting the lantern before release",
                    visible_props="the glowing lantern, open sky, and a small source of flame",
                    instant_detail="show one exact moment when the lantern first glows and the launch is about to begin",
                ),
                ShotSpec(
                    location="the same open night space with clear sky above",
                    subject_pose="tilts the head up with arms or paws just opening away from the lantern",
                    primary_action="releasing the lantern into the sky",
                    visible_props="the lantern lifting upward and open dark sky",
                    instant_detail="freeze the split second when the lantern leaves the subject's hands",
                ),
                ShotSpec(
                    location="the lantern launch site under a calm night sky",
                    subject_pose="stands still and looks upward with a relaxed expression",
                    primary_action="watching the lantern drift higher after release",
                    visible_props="the floating lantern, night sky, and quiet ground below",
                    instant_detail="capture one resolved instant after the successful launch, not the whole flight",
                ),
            ]
            return self._panel_specs_from_beats(context, request, JOURNEY_BEATS, scenes)
        setting_hint = context.semantics.setting_hint or "a visible route ahead"
        object_hint = context.semantics.primary_object or "the goal of the journey"
        scenes = [
            ShotSpec(
                location=setting_hint,
                subject_pose="faces forward from a clear starting point with the body ready to move",
                primary_action=f"setting out to begin {context.semantics.activity or context.normalized_theme}",
                visible_props=f"a visible route and a clear direction toward {object_hint}",
                instant_detail="freeze the first committed instant of departure",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="halts or braces mid-movement as progress gets interrupted",
                primary_action=f"meeting the first obstacle while trying to continue {context.semantics.activity or 'the journey'}",
                visible_props=f"a visible obstacle and interrupted progress toward {object_hint}",
                instant_detail="show one exact encounter instant instead of several travel moments",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="leans into a new approach with visible effort",
                primary_action=f"changing approach to push through toward {object_hint}",
                visible_props=f"the route ahead and one clear sign of effort or momentum change near {object_hint}",
                instant_detail="freeze the turning-point instant when the new approach starts to work",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="comes to a brief stop after reaching the goal",
                primary_action=f"taking in the resolved outcome near {object_hint}",
                visible_props=f"the reached goal, the finished route, and a clear sense of arrival near {object_hint}",
                instant_detail="capture one precise arrival instant after the journey succeeds",
            ),
        ]
        return self._panel_specs_from_beats(context, request, JOURNEY_BEATS, scenes)

    def _build_problem_solving_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        object_hint = context.semantics.primary_object
        if object_hint in {"灯", "lights", "light", "street lights", "city lights"}:
            scenes = [
                ShotSpec(
                    location="a dark city street where the lamps have gone out",
                    subject_pose="looks upward from the street with concern",
                    primary_action="realizing the street lights are dark",
                    visible_props="unlit lamps, dim buildings, and a shadowed street",
                    instant_detail="freeze the first instant the subject notices the blackout above",
                ),
                ShotSpec(
                    location="the same city block near poles, wires, or a control box",
                    subject_pose="leans in close to inspect the failing system",
                    primary_action="searching for the cause of the lighting failure",
                    visible_props="wires, lamp posts, panels, or exposed equipment",
                    instant_detail="show one exact inspection moment with attention on one clue",
                ),
                ShotSpec(
                    location="the repair point on the lighting system",
                    subject_pose="works close to the broken part with focused hands",
                    primary_action="repairing the lighting system",
                    visible_props="tools, wires, a broken part, and the first returning glow",
                    instant_detail="freeze the decisive repair instant when the fix starts to take effect",
                ),
                ShotSpec(
                    location="the city street after the lights return",
                    subject_pose="stands beneath the restored lamps with a released posture",
                    primary_action="seeing the street come back to life",
                    visible_props="glowing street lamps, bright windows, and a restored street",
                    instant_detail="capture one immediate payoff moment after the lights switch back on",
                ),
            ]
            return self._panel_specs_from_beats(context, request, PROBLEM_SOLVING_BEATS, scenes)
        if object_hint in {"钥匙", "key", "keys"}:
            scenes = [
                ShotSpec(
                    location="a doorway or bag-drop area",
                    subject_pose="looks down at an empty hand or open bag with sudden concern",
                    primary_action="realizing the key is missing",
                    visible_props="an empty hand, a bag or doorway, and the absent key's usual place",
                    instant_detail="freeze the exact moment of noticing the key is gone",
                ),
                ShotSpec(
                    location="a cluttered room corner, floor edge, or plant area",
                    subject_pose="leans low while scanning one narrow area closely",
                    primary_action="searching under furniture or beside objects for the key",
                    visible_props="furniture legs, floor edges, plants, or small hiding places",
                    instant_detail="show one exact search instant in one concentrated area",
                ),
                ShotSpec(
                    location="the small hidden corner where the key appears",
                    subject_pose="reaches toward the newly spotted key",
                    primary_action="recovering the missing key",
                    visible_props="the visible key and the tight place where it was hidden",
                    instant_detail="freeze the split second when the key is finally seen and reached for",
                ),
                ShotSpec(
                    location="the original entry area after the search ends",
                    subject_pose="holds the key up with visible relief",
                    primary_action="showing the recovered key after the problem is resolved",
                    visible_props="the key in hand and a now-settled doorway or bag",
                    instant_detail="capture one resolved instant with the key clearly back in hand",
                ),
            ]
            return self._panel_specs_from_beats(context, request, PROBLEM_SOLVING_BEATS, scenes)

        activity_hint = context.semantics.activity or "solve the problem"
        object_label = context.semantics.primary_object or "the problem source"
        setting_hint = context.semantics.setting_hint or "the immediate surroundings"
        scenes = [
            ShotSpec(
                location=setting_hint,
                subject_pose="stops in front of the visible issue with attention fixed on it",
                primary_action=f"facing the immediate problem while trying to {activity_hint}",
                visible_props=f"the issue around {object_label} and the nearby surroundings",
                instant_detail="freeze one exact instant when the problem becomes obvious",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="leans in or moves around while checking one clue after another",
                primary_action=f"searching for the cause or missing piece needed to {activity_hint}",
                visible_props=f"visible clues and the part of {object_label} being investigated",
                instant_detail="show one exact investigation instant, not the whole search process",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="focuses tightly on the fix with careful hands or tools",
                primary_action=f"trying the solution to fix {object_label}",
                visible_props=f"the fix in progress and visible change around {object_label}",
                instant_detail="freeze the decisive instant when the solution is actively being applied",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="relaxes after seeing the outcome clearly improve",
                primary_action=f"seeing the problem resolved around {object_label}",
                visible_props=f"the corrected {object_label} and a visibly improved setting",
                instant_detail="capture one payoff instant after the solution succeeds",
            ),
        ]
        return self._panel_specs_from_beats(context, request, PROBLEM_SOLVING_BEATS, scenes)

    def _build_competition_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        sport_label = self._competition_activity_label(context.normalized_theme)
        venue_label = self._competition_venue_label(context.normalized_theme)
        decisive_action = self._competition_decisive_action(context.normalized_theme)
        scenes = [
            ShotSpec(
                location=venue_label,
                subject_pose="waits at the sideline with the body squared toward the court",
                primary_action=f"holding the ball before the {sport_label} reaches its decisive stretch",
                visible_props="one ball, the court lines, and the competition setting",
                instant_detail="freeze the pre-play instant just before the decisive action begins",
            ),
            ShotSpec(
                location=venue_label,
                subject_pose="drops low into a protective dribble stance",
                primary_action=f"dribbling near the three-point line while one defender reaches in from the side during the {sport_label}",
                visible_props="one ball, one nearby defender, and the three-point line",
                instant_detail="show one tense on-court instant under pressure rather than a sequence of moves",
            ),
            ShotSpec(
                location=venue_label,
                subject_pose="extends upward through the shot release with full concentration",
                primary_action=f"releasing {decisive_action}",
                visible_props="the ball leaving the hands and the hoop in the same view",
                instant_detail="freeze the split second when the decisive shot leaves the subject's hands",
            ),
            ShotSpec(
                location=venue_label,
                subject_pose="reacts immediately after the result becomes clear",
                primary_action=f"watching the ball drop through the hoop as the {sport_label} turns in a winning direction",
                visible_props="the hoop, the ball at the rim or net, and immediate celebration",
                instant_detail="capture one instant of result and reaction, not a montage of the full finish",
            ),
        ]
        return self._panel_specs_from_beats(context, request, COMPETITION_BEATS, scenes)

    def _build_fallback_panels(self, context: PlanningContext, request: ComicRequest) -> list[PanelSpec]:
        if context.semantics.activity in {"做饭", "烹饪", "cook", "cooking"}:
            scenes = [
                ShotSpec(
                    location="a small kitchen workspace",
                    subject_pose="stands close to the counter with the recipe held or studied carefully",
                    primary_action="studying the recipe before cooking begins",
                    visible_props="a recipe, bowls, ingredients, and a clear kitchen counter",
                    instant_detail="freeze the exact instant when the subject compares the ingredients to the recipe",
                ),
                ShotSpec(
                    location="the same kitchen counter",
                    subject_pose="jerks back slightly as the work goes wrong",
                    primary_action="making a messy mistake while chopping or mixing",
                    visible_props="spilled ingredients, tools, and the half-prepared food",
                    instant_detail="show one exact mistake moment instead of several cooking steps",
                ),
                ShotSpec(
                    location="the stove or pan area of the kitchen",
                    subject_pose="leans in with renewed focus over the pan or recipe",
                    primary_action="trying again carefully while stirring or adjusting the recipe",
                    visible_props="a pan, utensils, steam or heat, and the recipe nearby",
                    instant_detail="freeze the instant of careful correction as the second attempt starts to work",
                ),
                ShotSpec(
                    location="the table or serving area after cooking",
                    subject_pose="presents the finished dish with visible pride",
                    primary_action="serving the completed meal",
                    visible_props="the plated food, tableware, and a clean serving surface",
                    instant_detail="capture one clear serving moment after the cooking succeeds",
                ),
            ]
            return self._panel_specs_from_beats(context, request, FALLBACK_BEATS, scenes)
        if context.semantics.primary_object in {"滑板", "skateboard"}:
            scenes = [
                ShotSpec(
                    location="an open practice area with smooth ground",
                    subject_pose="places weight carefully onto the board for the first time",
                    primary_action="testing the skateboard with a tentative first step",
                    visible_props="one skateboard and clear open ground",
                    instant_detail="freeze the first uncertain instant of getting onto the board",
                ),
                ShotSpec(
                    location="the same practice area mid-attempt",
                    subject_pose="tilts off balance with arms or body reacting to the wobble",
                    primary_action="losing balance on the moving skateboard",
                    visible_props="the board underfoot and unstable motion across the ground",
                    instant_detail="show one exact wobble moment with the risk of falling",
                ),
                ShotSpec(
                    location="the practice area just after the wobble",
                    subject_pose="bends low and centers the body over the board",
                    primary_action="regaining balance while pushing forward again",
                    visible_props="the board, the ground, and a visible recovery in posture",
                    instant_detail="freeze the turning instant when balance comes back under control",
                ),
                ShotSpec(
                    location="the same open area after practice clicks",
                    subject_pose="rides forward with a relaxed, stable stance",
                    primary_action="gliding smoothly with new confidence",
                    visible_props="the skateboard moving cleanly across open ground",
                    instant_detail="capture one smooth success instant after the recovery pays off",
                ),
            ]
            return self._panel_specs_from_beats(context, request, FALLBACK_BEATS, scenes)
        activity_hint = context.semantics.activity or "deal with the situation"
        object_hint = context.semantics.primary_object or "the immediate focus"
        setting_hint = context.semantics.setting_hint or "the current place"
        scenes = [
            ShotSpec(
                location=setting_hint,
                subject_pose="holds a clear starting posture with attention on the immediate task",
                primary_action=f"beginning to {activity_hint}",
                visible_props=f"the immediate focus on {object_hint} within {setting_hint}",
                instant_detail="freeze the opening instant when the task first begins",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="reacts visibly as the task gets interrupted",
                primary_action=f"hitting a visible complication while trying to {activity_hint}",
                visible_props=f"the obstacle around {object_hint} and the interrupted task",
                instant_detail="show one exact complication moment rather than a sequence of setbacks",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="commits to one visible response with deliberate movement",
                primary_action=f"taking a specific response that changes what happens next while trying to {activity_hint}",
                visible_props=f"the response in action and the still-visible focus on {object_hint}",
                instant_detail="freeze the moment when the response starts to change the outcome",
            ),
            ShotSpec(
                location=setting_hint,
                subject_pose="settles after the effort with the result now visible",
                primary_action=f"reaching the final outcome after the response helps complete {activity_hint}",
                visible_props=f"the completed outcome around {object_hint} in the same setting",
                instant_detail="capture one resolved payoff instant after the task succeeds",
            ),
        ]
        return self._panel_specs_from_beats(context, request, FALLBACK_BEATS, scenes)

    def _panel_specs_from_beats(
        self,
        context: PlanningContext,
        request: ComicRequest,
        beats: list[BeatSpec],
        scenes: list[ShotSpec],
    ) -> list[PanelSpec]:
        panels: list[PanelSpec] = []
        for index, beat in enumerate(beats, start=1):
            shot = scenes[index - 1]
            scene_description = (
                f"In {shot.location}, {context.subject} {shot.subject_pose} while {shot.primary_action}; "
                f"{shot.instant_detail}."
            )
            visual_description = (
                f"Show {context.subject} in one clear view with {shot.visible_props} in {shot.location}; "
                f"{shot.instant_detail}."
            )
            panels.append(
                PanelSpec(
                    index=index,
                    caption=beat.caption,
                    dialogue=_dialogue_for_panel(index, context.subject),
                    scene_description=scene_description,
                    action=shot.primary_action.capitalize(),
                    emotion=beat.emotion,
                    camera_framing="medium shot" if index == 1 and beat.camera_framing == "wide shot" else beat.camera_framing,
                    visual_description=visual_description,
                    generated_prompt_base="",
                    final_image_prompt="",
                    prompt_source="generated",
                    input_mode="reference_guided" if request.reference_image_path else "text_only",
                )
            )
        return panels

    def _resolve_subject(self, explicit_character: str | None, normalized_theme: str) -> str:
        if explicit_character:
            return explicit_character.strip()

        for candidate in SPECIFIC_SUBJECT_PATTERNS:
            if candidate in normalized_theme:
                return candidate

        regex_patterns = [
            r"同一只([^在，。,.]+)",
            r"记录([^在，。,.]+)在",
            r"一只([^在的，。,.]+?)(?:在|的)",
            r"about ([^,.]+)",
        ]
        for pattern in regex_patterns:
            match = re.search(pattern, normalized_theme, re.IGNORECASE)
            if match:
                candidate = self._normalize_subject(match.group(1).strip())
                if candidate:
                    return candidate

        lowered = normalized_theme.lower()
        for candidate in GENERIC_SUBJECT_PATTERNS:
            if candidate in lowered:
                return candidate
        return "main character"

    def _detect_intent(self, normalized_theme: str, semantics: ThemeSemantics) -> str:
        lowered = normalized_theme.lower()
        if (
            "四季" in normalized_theme
            or "春夏秋冬" in normalized_theme
            or all(word in lowered for word in ("spring", "summer", "autumn", "winter"))
            or all(cue in semantics.temporal_cues for cue in ("spring", "summer", "autumn", "winter"))
        ):
            return "seasonal_progression"
        if any(term in normalized_theme for term in ("上学", "学校", "一天", "放学")) or any(
            term in lowered for term in ("school", "day in the life")
        ) or "school" in semantics.domain_cues:
            return "day_in_the_life"
        if any(term in normalized_theme for term in ("修好", "修理", "找回", "寻找", "丢失", "钥匙")) or any(
            term in lowered for term in ("fix", "repair", "search", "find", "lost", "solve")
        ) or "problem_solving" in semantics.domain_cues:
            return "problem_solving"
        if any(term in normalized_theme for term in ("比赛", "球赛", "篮球赛", "足球赛", "决赛", "绝杀", "冠军", "夺冠")) or any(
            term in lowered for term in ("game", "match", "tournament", "final", "winner", "championship", "buzzer-beater")
        ) or "competition" in semantics.domain_cues:
            return "competition_climax"
        if any(term in normalized_theme for term in ("旅程", "变化", "成长", "放飞", "冒险")) or any(
            term in lowered for term in ("progression", "transformation", "journey", "growth", "travel", "travels", "adventure", "lantern")
        ) or "journey" in semantics.domain_cues:
            return "journey_adventure"
        return "fallback_story"

    def _parse_theme_semantics(self, normalized_theme: str, subject: str) -> ThemeSemantics:
        lowered = normalized_theme.lower()
        subjectless = normalized_theme.replace(subject, " ").strip(" ，。,.")
        activity = self._extract_activity(subjectless, lowered)
        primary_object = self._extract_primary_object(normalized_theme, lowered)
        setting_hint = self._extract_setting_hint(normalized_theme, lowered)
        temporal_cues = self._extract_temporal_cues(normalized_theme, lowered)
        domain_cues = self._extract_domain_cues(normalized_theme, lowered, activity, primary_object, temporal_cues)
        return ThemeSemantics(
            subject=subject,
            activity=activity,
            primary_object=primary_object,
            setting_hint=setting_hint,
            temporal_cues=temporal_cues,
            domain_cues=domain_cues,
        )

    def _extract_activity(self, subjectless: str, lowered: str) -> str:
        activity_map = [
            (("上学", "school"), "go to school"),
            (("放飞", "release", "launch"), "release a lantern"),
            (("做饭", "烹饪", "cook"), "cook"),
            (("修好", "修理", "repair", "fix"), "repair"),
            (("找回", "寻找", "find", "search"), "find"),
            (("成长", "growth"), "grow"),
            (("旅程", "journey", "travel", "travels"), "travel"),
            (("比赛", "球赛", "basketball", "football", "soccer", "match", "game"), "compete"),
        ]
        for terms, label in activity_map:
            if any(term in subjectless or term in lowered for term in terms):
                return label
        cleaned = re.sub(r"[，。,.]", " ", subjectless)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or "act"

    def _extract_primary_object(self, normalized_theme: str, lowered: str) -> str:
        object_map = [
            (("灯笼", "lantern"), "灯笼"),
            (("钥匙", "key", "keys"), "钥匙"),
            (("灯", "lights", "light"), "灯"),
            (("滑板", "skateboard"), "滑板"),
            (("篮球", "basketball"), "篮球"),
            (("足球", "football", "soccer"), "足球"),
            (("食谱", "recipe"), "食谱"),
            (("城市", "city"), "城市"),
        ]
        for terms, label in object_map:
            if any(term in normalized_theme or term in lowered for term in terms):
                return label
        return ""

    def _extract_setting_hint(self, normalized_theme: str, lowered: str) -> str:
        setting_map = [
            (("学校", "classroom", "school"), "a school route and classroom setting"),
            (("城市", "street", "city"), "a city street setting"),
            (("厨房", "kitchen"), "a kitchen workspace"),
            (("球场", "court", "stadium"), "a competition venue"),
            (("夜空", "night sky", "sky"), "an open outdoor sky"),
            (("路", "road"), "a road or path forward"),
        ]
        for terms, label in setting_map:
            if any(term in normalized_theme or term in lowered for term in terms):
                return label
        return ""

    def _extract_temporal_cues(self, normalized_theme: str, lowered: str) -> tuple[str, ...]:
        cues: list[str] = []
        cue_map = [
            (("春", "spring"), "spring"),
            (("夏", "summer"), "summer"),
            (("秋", "autumn", "fall"), "autumn"),
            (("冬", "winter"), "winter"),
            (("早晨", "清晨", "morning"), "morning"),
            (("傍晚", "evening", "sunset"), "evening"),
            (("一天", "day"), "day"),
        ]
        for terms, label in cue_map:
            if any(term in normalized_theme or term in lowered for term in terms):
                cues.append(label)
        return tuple(dict.fromkeys(cues))

    def _extract_domain_cues(
        self,
        normalized_theme: str,
        lowered: str,
        activity: str,
        primary_object: str,
        temporal_cues: tuple[str, ...],
    ) -> tuple[str, ...]:
        cues: list[str] = []
        if "school" in activity or any(term in normalized_theme for term in ("上学", "学校", "放学")):
            cues.append("school")
        if primary_object in {"灯", "钥匙"} or any(term in lowered for term in ("repair", "fix", "search", "find", "lost")):
            cues.append("problem_solving")
        if primary_object == "灯笼" or any(term in lowered for term in ("journey", "travel", "adventure", "release")):
            cues.append("journey")
        if any(term in normalized_theme for term in ("比赛", "绝杀", "篮球赛", "足球赛")) or any(
            term in lowered for term in ("game", "match", "basketball", "soccer", "football")
        ):
            cues.append("competition")
        if all(cue in temporal_cues for cue in ("spring", "summer", "autumn", "winter")) or "四季" in normalized_theme:
            cues.append("seasonal")
        return tuple(dict.fromkeys(cues))

    def _normalize_subject(self, value: str) -> str:
        for candidate in SPECIFIC_SUBJECT_PATTERNS:
            if candidate in value:
                return candidate
        keyword_spans = [
            "青蛙",
            "蛙",
            "熊",
            "乌鸦",
            "浣熊",
            "乌龟",
            "鼹鼠",
            "机器人",
            "小男孩",
            "小女孩",
        ]
        for keyword in keyword_spans:
            if keyword in value:
                return value[: value.index(keyword) + len(keyword)]
        return value.strip()

    def _competition_activity_label(self, normalized_theme: str) -> str:
        lowered = normalized_theme.lower()
        if "篮球" in normalized_theme or "basketball" in lowered:
            return "basketball game"
        if "足球" in normalized_theme or "soccer" in lowered or "football" in lowered:
            return "football match"
        if "网球" in normalized_theme or "tennis" in lowered:
            return "tennis match"
        return "competition"

    def _competition_venue_label(self, normalized_theme: str) -> str:
        lowered = normalized_theme.lower()
        if "篮球" in normalized_theme or "basketball" in lowered:
            return "an indoor basketball court"
        if "足球" in normalized_theme or "soccer" in lowered or "football" in lowered:
            return "a crowded stadium field"
        if "网球" in normalized_theme or "tennis" in lowered:
            return "a bright tennis court"
        return "a lively competition venue"

    def _competition_decisive_action(self, normalized_theme: str) -> str:
        lowered = normalized_theme.lower()
        if "绝杀三分" in normalized_theme:
            return "a game-winning three-point shot"
        if "绝杀" in normalized_theme:
            return "the game-winning decisive play"
        if "投进" in normalized_theme and "三分" in normalized_theme:
            return "a high-pressure three-point shot"
        if "进球" in normalized_theme or "score" in lowered:
            return "the scoring move that can decide the contest"
        return "the decisive winning play"


class LMStoryPlanner:
    def __init__(self) -> None:
        self.api_url = os.getenv(COMIC_AGENT_LM_API_URL_ENV, "").strip()
        self.api_key = os.getenv(COMIC_AGENT_LM_API_KEY_ENV, "").strip()
        self.model = os.getenv(COMIC_AGENT_LM_MODEL_ENV, "").strip()
        self.timeout_seconds = _read_timeout_seconds()

    def plan(self, request: ComicRequest) -> StoryStructure:
        try:
            self.validate_configuration()
            payload = self._request_payload(request)
            story = validate_lm_storyboard_payload(payload, request)
        except LMPlanningError:
            raise
        except TimeoutError as exc:
            raise LMPlanningError("LM-assisted planning timed out") from exc
        except Exception as exc:
            raise LMPlanningError("LM-assisted planning was unavailable") from exc
        return story

    def validate_configuration(self) -> LMConfiguration:
        missing: list[str] = []
        if not self.api_url:
            missing.append(COMIC_AGENT_LM_API_URL_ENV)
        if not self.api_key:
            missing.append(COMIC_AGENT_LM_API_KEY_ENV)
        if not self.model:
            missing.append(COMIC_AGENT_LM_MODEL_ENV)
        if missing:
            missing_list = ", ".join(missing)
            raise LMPlanningError(f"LM-assisted planning configuration is incomplete. Missing environment variables: {missing_list}")
        return LMConfiguration(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
        )

    def _request_payload(self, request: ComicRequest) -> dict[str, object] | str:
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a story planner for a four-panel comic pipeline. "
                        "Return exactly one strict JSON object and nothing else."
                    ),
                },
                {"role": "user", "content": _build_lm_prompt(request)},
            ],
            "response_format": {"type": "json_object"},
        }
        http_request = Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_text = response.read().decode("utf-8")
        except HTTPError as exc:
            raise LMPlanningError(f"LM-assisted planning request failed with status {exc.code}") from exc
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, TimeoutError):
                raise LMPlanningError("LM-assisted planning timed out") from exc
            raise LMPlanningError("LM-assisted planning was unavailable") from exc
        return _extract_lm_payload(response_text)


def validate_lm_storyboard_payload(payload: dict[str, object] | str, request: ComicRequest) -> StoryStructure:
    parsed = payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise LMPlanningError("LM-assisted storyboard planning returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise LMPlanningError("LM-assisted storyboard planning did not return one JSON object")

    for field_name in LM_REQUIRED_STORYBOARD_FIELDS:
        if field_name not in parsed:
            raise LMPlanningError(f"LM-assisted storyboard planning is missing required field: {field_name}")

    subject = str(parsed["subject"]).strip()
    explicit_character = request.character.strip() if request.character else ""
    if explicit_character and subject and subject != explicit_character:
        raise LMPlanningError("LM-assisted storyboard planning subject conflicts with explicit character input")
    if not explicit_character and not subject:
        raise LMPlanningError("LM-assisted storyboard planning result is missing a subject")

    panels_payload = parsed["panels"]
    if not isinstance(panels_payload, list):
        raise LMPlanningError("LM-assisted storyboard planning field panels must be a JSON array")
    if len(panels_payload) != 4:
        raise LMPlanningError("LM-assisted storyboard planning must return exactly 4 panels")

    panels: list[PanelSpec] = []
    for index, panel_payload in enumerate(panels_payload, start=1):
        if not isinstance(panel_payload, dict):
            raise LMPlanningError("LM-assisted storyboard planning panels must contain JSON objects")
        panel_values: dict[str, str] = {}
        for field_name in LM_REQUIRED_PANEL_FIELDS:
            if field_name not in panel_payload:
                raise LMPlanningError(f"LM-assisted storyboard planning panel {index} is missing required field: {field_name}")
            value = str(panel_payload[field_name]).strip()
            if not value:
                raise LMPlanningError(f"LM-assisted storyboard planning panel {index} field {field_name} cannot be empty")
            if _contains_rejected_layout_content(value):
                raise LMPlanningError("LM-assisted storyboard planning includes page-level or multi-panel instructions")
            panel_values[field_name] = value

        panels.append(
            PanelSpec(
                index=index,
                caption=panel_values["caption"],
                dialogue=panel_values["dialogue"],
                scene_description=panel_values["scene_description"],
                action=panel_values["action"],
                emotion=panel_values["emotion"],
                camera_framing=panel_values["camera_framing"],
                visual_description=panel_values["visual_description"],
                generated_prompt_base="",
                final_image_prompt="",
                prompt_source="generated",
                input_mode="reference_guided" if request.reference_image_path else "text_only",
            )
        )

    resolved_subject = explicit_character or subject
    return StoryStructure(
        title=f"Story sequence: {request.theme}",
        premise=f"A four-step visual story about {request.theme} featuring {resolved_subject}.",
        panels=panels,
        subject=resolved_subject,
    )


def _contains_rejected_layout_content(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in REJECTED_LAYOUT_TERMS)


def _extract_lm_payload(response_text: str) -> dict[str, object] | str:
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text
    if isinstance(parsed, dict) and "subject" in parsed and "panels" in parsed:
        return parsed
    if isinstance(parsed, dict):
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                fragments: list[str] = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        fragments.append(str(item["text"]))
                if fragments:
                    return "\n".join(fragments)
        output = parsed.get("output")
        if isinstance(output, dict):
            text = output.get("text") or output.get("content")
            if isinstance(text, str):
                return text
    return parsed


def _build_lm_prompt(request: ComicRequest) -> str:
    explicit_character = request.character.strip() if request.character else ""
    character_line = f'Use "{explicit_character}" as the subject.' if explicit_character else "Infer one main subject."
    return "\n".join(
        [
            "Expand the theme into exactly four storyboard panels for a four-panel comic pipeline.",
            f"Theme: {request.theme}",
            character_line,
            "Return exactly one strict JSON object with keys: subject, panels.",
            "panels must be a JSON array with exactly 4 objects.",
            "Each panel object must contain: caption, dialogue, scene_description, action, emotion, camera_framing, visual_description.",
            "Each panel must describe one concrete single-scene visual moment only.",
            "Respect explicit panel ordering signals in the theme, including first/second/third/fourth and 第一格/第二格/第三格/第四格.",
            "Do not merge multiple panel beats into one panel.",
            "Do not describe a collage, split-screen, grid, montage, comparison sheet, or comic page in any field.",
            "Do not include markdown, code fences, or extra explanation.",
        ]
    )


class StoryPlannerAgent(StoryboardAgent):
    """Backward-compatible alias for older planner references."""


def _read_timeout_seconds() -> float:
    raw_timeout = os.getenv(COMIC_AGENT_LM_TIMEOUT_ENV, "").strip()
    if not raw_timeout:
        return DEFAULT_LM_TIMEOUT_SECONDS
    try:
        timeout = float(raw_timeout)
    except ValueError:
        return DEFAULT_LM_TIMEOUT_SECONDS
    return timeout if timeout > 0 else DEFAULT_LM_TIMEOUT_SECONDS


def _dialogue_for_panel(index: int, subject: str) -> str:
    dialogues = {
        1: f"{subject} notices something important.",
        2: f"{subject} says, 'This got harder than expected.'",
        3: f"{subject} says, 'I can still make this work.'",
        4: f"{subject} says, 'That turned out better than I hoped.'",
    }
    return dialogues[index]
