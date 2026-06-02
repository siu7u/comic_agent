from __future__ import annotations

import argparse
from pathlib import Path

from comic_agent.models.comic_request import ComicRequest
from comic_agent.pipeline.prompt_builder import (
    build_character_bible,
    build_style_bible,
    populate_panel_prompts,
)
from comic_agent.pipeline.story_planner import StoryboardAgent, plan_story


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="probe_storyboard_prompts",
        description="Inspect StoryboardAgent panel beats and final provider-facing prompts without calling any image provider.",
    )
    parser.add_argument("--theme", required=True)
    parser.add_argument("--character")
    parser.add_argument("--style")
    parser.add_argument("--image-prompt")
    parser.add_argument("--planner", choices=["rule_based", "lm_assisted"])
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--out", default="output/probe-storyboard")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    request = ComicRequest(
        theme=args.theme.strip(),
        planner_mode=args.planner,
        character=args.character.strip() if args.character else None,
        style=args.style.strip() if args.style else None,
        image_prompt=args.image_prompt.strip() if args.image_prompt else None,
        lang=args.lang,
        output_dir=Path(args.out),
    )

    context = StoryboardAgent().build_context(request)
    story, planner_run = plan_story(request)
    character_bible = build_character_bible(request, subject_override=story.subject)
    style_bible = build_style_bible(request)
    story, warnings = populate_panel_prompts(story, request, character_bible, style_bible)

    print(f"theme: {request.theme}")
    print(f"planner_requested: {request.planner_mode}")
    print(f"planner_actual: {planner_run.actual_mode}")
    if planner_run.fallback_triggered:
        print(f"planner_fallback_reason: {planner_run.fallback_reason}")
    print(f"subject: {context.subject}")
    print(f"intent_type: {context.intent_type}")
    print(f"semantic_activity: {context.semantics.activity}")
    print(f"semantic_object: {context.semantics.primary_object}")
    print(f"semantic_setting: {context.semantics.setting_hint}")
    print(f"semantic_temporal_cues: {list(context.semantics.temporal_cues)}")
    print(f"semantic_domain_cues: {list(context.semantics.domain_cues)}")
    print(f"character_bible: {character_bible.summary}")
    print(f"style_bible: {style_bible.style_name}")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    print()

    for panel in story.panels:
        print(f"=== Panel {panel.index}: {panel.caption} ===")
        print(f"dialogue: {panel.dialogue}")
        print(f"scene_description: {panel.scene_description}")
        print(f"action: {panel.action}")
        print(f"emotion: {panel.emotion}")
        print(f"camera_framing: {panel.camera_framing}")
        print(f"visual_description: {panel.visual_description}")
        print("final_image_prompt:")
        print(panel.final_image_prompt)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
