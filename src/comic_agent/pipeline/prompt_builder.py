from __future__ import annotations

import re

from comic_agent.models.bibles import CharacterBible, StyleBible
from comic_agent.models.comic_request import ComicRequest
from comic_agent.models.panel import StoryStructure
from comic_agent.pipeline.safety import rewrite_for_consistency, sanitize_guidance
from comic_agent.pipeline.story_planner import resolve_story_subject

SINGLE_PANEL_CONSTRAINTS = [
    "single full-frame illustration",
    "one scene only",
    "one subject occurrence unless another character is explicitly described",
    "one continuous moment",
    "freeze one exact instant",
    "one location only",
    "one undivided image",
    "no before-and-after sequence",
    "do not split the image into sections",
    "do not draw multiple frames or multiple scenes in one image",
    "no collage",
    "no split-screen",
    "no grid",
    "no divided layout",
    "no sub-images",
    "no montage",
    "no comparison sheet",
    "no text labels",
    "no captions",
    "no speech bubbles",
]

LAYOUT_PHRASES = (
    "fixed comic readability",
    "panel-to-panel continuity",
    "four-panel visual language",
    "four-panel layout",
    "multiple panels",
    "multi-panel",
    "comic layout",
    "sub-images",
    "comparison sheet",
    "split-screen",
    "seasonal comparison layout",
    "montage layout",
)

def build_character_bible(request: ComicRequest, subject_override: str | None = None) -> CharacterBible:
    summary = _character_summary(request, subject_override)
    appearance_traits = _appearance_traits(summary)
    if request.reference_image_path:
        appearance_traits.append("maintain reference-image silhouette cues")
    return CharacterBible(
        summary=summary,
        appearance_traits=appearance_traits,
        personality_notes=["readable silhouette", "consistent face, body size, and markings in every panel"],
        consistency_rules=["keep the same character identity, markings, and proportions"],
    )


def build_style_bible(request: ComicRequest) -> StyleBible:
    style_name = request.style or "storybook illustration"
    tone = _strip_layout_phrases(request.image_prompt or f"tone consistent with {request.theme}")
    return StyleBible(
        style_name=style_name,
        tone=tone,
        composition_rules=["single-scene composition", "clear subject focus"],
        rendering_traits=[style_name, "full-frame illustration"],
    )


def populate_panel_prompts(
    story: StoryStructure,
    request: ComicRequest,
    character_bible: CharacterBible,
    style_bible: StyleBible,
) -> tuple[StoryStructure, list[str]]:
    request_warnings: list[str] = []
    required_fragments = [
        f"The main subject is {character_bible.summary}.",
        f"Render it as {style_bible.style_name}.",
        f"The overall tone is {style_bible.tone}.",
    ]
    for panel in story.panels:
        base_prompt = _build_provider_prompt(panel, request, character_bible, style_bible)
        panel.generated_prompt_base = base_prompt
        prompt_text = base_prompt
        source = "generated"

        if request.image_prompt:
            global_text, warnings = sanitize_guidance(request.image_prompt, "global image prompt")
            global_text = _strip_layout_phrases(global_text)
            prompt_text = f"{prompt_text}\nAdditional guidance: {global_text}."
            request_warnings.extend(warnings)
            source = "merged"

        panel_prompt = request.panel_prompts.get(panel.index)
        if panel_prompt:
            user_text, warnings = sanitize_guidance(panel_prompt, f"panel {panel.index} prompt")
            user_text = _strip_layout_phrases(user_text)
            prompt_text = f"{prompt_text}\nPanel-specific guidance: {user_text}."
            request_warnings.extend(warnings)
            source = "user_guided"

        prompt_text, consistency_warnings = rewrite_for_consistency(
            prompt_text,
            required_fragments,
            f"panel {panel.index} prompt",
        )
        panel.warnings.extend(consistency_warnings)
        request_warnings.extend(consistency_warnings)
        panel.final_image_prompt = prompt_text
        panel.prompt_source = source
    return story, _dedupe(request_warnings)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _character_summary(request: ComicRequest, subject_override: str | None = None) -> str:
    return (subject_override or resolve_story_subject(request)).strip()


def _appearance_traits(summary: str) -> list[str]:
    traits: list[str] = []
    lowered = summary.lower()
    if "橘猫" in summary or "orange cat" in lowered or "tabby" in lowered:
        traits.append("orange tabby coat with visible stripes")
    if "流浪" in summary or "stray" in lowered:
        traits.append("slightly scruffy fur and alert street-cat posture")
    if "猫" in summary or "cat" in lowered:
        traits.append("triangular ears, whiskers, and a long tail")
    if "兔" in summary or "rabbit" in lowered:
        traits.append("long ears, soft fur, and a compact muzzle")
    if "狐" in summary or "fox" in lowered:
        traits.append("orange fur, pointed ears, and a bushy tail")
    if "蛙" in summary or "frog" in lowered:
        traits.append("round eyes, smooth green skin, and compact body shape")
    if "熊" in summary or "bear" in lowered:
        traits.append("broad body, rounded ears, and sturdy paws")
    if not traits:
        traits.append(f"distinctive visual traits matching {summary}")
    traits.append("consistent facial markings and body proportions")
    return _dedupe(traits)


def _strip_layout_phrases(text: str) -> str:
    cleaned = text
    for phrase in LAYOUT_PHRASES:
        pattern = re.compile(rf"(?<!no )(?<!without ){re.escape(phrase)}", re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)
    cleaned = re.sub(r"\b(and|with)\s*(?=[;,.]|$)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s*;\s*;\s*", "; ", cleaned)
    return cleaned.strip(" ;,")


def _build_provider_prompt(panel, request: ComicRequest, character_bible: CharacterBible, style_bible: StyleBible) -> str:
    prompt_lines = [
        "Draw exactly one finished panel image.",
        "This prompt describes one panel only.",
        "Do not draw a full comic page, extra panels, repeated versions of the subject, or multiple story beats in one image.",
        "Create one full-frame illustration of a single moment.",
        "Show only one continuous scene in one undivided image.",
        "Freeze one exact instant instead of showing a sequence of events.",
        "Keep the subject in one location and do not repeat the subject in multiple places within the image.",
    ]
    if request.lang.lower().startswith("zh"):
        prompt_lines = [
            "只画一张完整单格插画。",
            "这条提示只描述当前这一格，不要画整页漫画、额外分格、多个连续场景，或同一主角的重复出现。",
            "不要补画前后剧情，不要把这一格扩成完整故事页。",
            f"当前这一格的场景是：{panel.scene_description}。",
            f"当前这一格的视觉重点是：{panel.visual_description}。",
            f"当前这一格的核心动作是：{panel.action}。",
            f"镜头类型固定为：{panel.camera_framing}。",
            *prompt_lines,
        ]
    if panel.index == 1:
        prompt_lines.extend(
            [
                "Show only the opening moment, not the whole story.",
                "Do not summarize later events from the story in this image.",
            ]
        )
    prompt_lines.extend(
        [
            f"The main subject is {character_bible.summary}.",
            f"Give the subject {_sentence_from_list(character_bible.appearance_traits)}.",
            f"Depict a scene where {panel.scene_description}.",
            f"Focus the image on this visual idea: {panel.visual_description}.",
            f"Capture this action: {panel.action}.",
            f"The emotional tone of the subject should feel {panel.emotion}.",
            f"Use {panel.camera_framing} framing.",
            f"Render it as {style_bible.style_name}.",
            f"The overall tone is {style_bible.tone}.",
            f"Keep visual consistency with {_sentence_from_list(character_bible.consistency_rules + style_bible.composition_rules)}.",
            f"Hard constraints: {_sentence_from_list(SINGLE_PANEL_CONSTRAINTS)}.",
        ]
    )
    return "\n".join(prompt_lines)


def _sentence_from_list(values: list[str]) -> str:
    cleaned = [value.strip().rstrip(".") for value in values if value.strip()]
    return "; ".join(cleaned)
