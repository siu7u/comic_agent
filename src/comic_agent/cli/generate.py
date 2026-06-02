from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from PIL import Image, UnidentifiedImageError

from comic_agent.models.comic_request import ComicRequest
from comic_agent.models.metadata import MetadataRecord, PanelAttemptTraceRecord, ProviderRunRecord
from comic_agent.models.panel import PanelAttemptRecord
from comic_agent.pipeline.composer import compose_final_comic
from comic_agent.pipeline.exporter import (
    build_artifact_set,
    default_output_dir,
    ensure_output_dir,
    save_final_comic,
    save_panel_images,
    write_metadata,
)
from comic_agent.pipeline.panel_validation import (
    SinglePanelHeuristicValidator,
    apply_retry_strategy,
    get_retry_strategies,
)
from comic_agent.pipeline.prompt_builder import (
    build_character_bible,
    build_style_bible,
    populate_panel_prompts,
)
from comic_agent.pipeline.safety import SafetyError, reject_unsafe_theme
from comic_agent.pipeline.story_planner import (
    SUPPORTED_PLANNER_MODES,
    plan_story,
)
from comic_agent.providers.base import ImageProvider, ProviderConfigurationError, ProviderGenerationError
from comic_agent.providers.mock import MockImageProvider
from comic_agent.providers.real_provider import WanxImageProvider


SUPPORTED_REFERENCE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
PROVIDER_FACTORIES = {
    "mock": MockImageProvider,
    "wanx": WanxImageProvider,
}

# The main entry point for the comic generation CLI tool.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comic-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--theme", required=True)
    generate.add_argument("--provider", choices=sorted(PROVIDER_FACTORIES), default="wanx")
    generate.add_argument("--planner", choices=sorted(SUPPORTED_PLANNER_MODES))
    generate.add_argument("--style")
    generate.add_argument("--character")
    generate.add_argument("--image-prompt")
    for idx in range(1, 5):
        generate.add_argument(f"--panel-prompt-{idx}")
    generate.add_argument("--reference-image")
    generate.add_argument("--lang", default="zh")
    generate.add_argument("--out")
    return parser


def parse_request(args: argparse.Namespace) -> ComicRequest:
    theme = args.theme.strip()
    if not theme:
        raise ValueError("Missing required input: --theme")
    panel_prompts: dict[int, str] = {}
    for idx in range(1, 5):
        value = getattr(args, f"panel_prompt_{idx}")
        if value:
            panel_prompts[idx] = value.strip()
    reference_path = validate_reference_image(args.reference_image) if args.reference_image else None
    output_dir = Path(args.out) if args.out else default_output_dir()
    return ComicRequest(
        theme=theme,
        provider=args.provider,
        planner_mode=args.planner,
        style=args.style.strip() if args.style else None,
        character=args.character.strip() if args.character else None,
        image_prompt=args.image_prompt.strip() if args.image_prompt else None,
        panel_prompts=panel_prompts,
        reference_image_path=reference_path,
        lang=args.lang,
        output_dir=output_dir,
    )


def validate_reference_image(raw_path: str | None) -> Path:
    if not raw_path:
        raise ValueError("Reference image path is required")
    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"Reference image cannot be read: {raw_path}")
    if path.suffix.lower() not in SUPPORTED_REFERENCE_SUFFIXES:
        raise ValueError(f"Unsupported reference image type: {path.suffix}")
    try:
        Image.open(path).verify()
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"Reference image cannot be read: {raw_path}") from exc
    return path


def load_dotenv(dotenv_path: Path | None = None) -> None:
    path = dotenv_path or (Path.cwd() / ".env")
    if not path.exists() or not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def run_generation(request: ComicRequest) -> MetadataRecord:
    reject_unsafe_theme(request.theme)
    ensure_output_dir(request.output_dir)
    story, planner_run = plan_story(request)
    character_bible = build_character_bible(request, subject_override=story.subject)
    style_bible = build_style_bible(request)
    story, request_warnings = populate_panel_prompts(story, request, character_bible, style_bible)
    provider = build_provider(request.provider)
    provider.validate_configuration()
    validator = SinglePanelHeuristicValidator()
    retry_strategies = get_retry_strategies()
    rendered_panels = []
    panel_attempt_traces: list[PanelAttemptTraceRecord] = []
    failure_message: str | None = None
    for panel in story.panels:
        last_error: Exception | None = None
        original_prompt = panel.final_image_prompt
        accepted = False
        for attempt, strategy in enumerate(retry_strategies):
            try:
                panel.provider_name = provider.name
                panel.provider_mode = provider.mode
                panel.retry_count = attempt
                panel.final_image_prompt = apply_retry_strategy(original_prompt, strategy)
                image = provider.generate_panel_image(panel)
                validation_result = validator.validate(image)
                panel.attempt_traces.append(
                    PanelAttemptRecord(
                        attempt_number=attempt + 1,
                        strategy_name=strategy.name,
                        generated_image_available=True,
                        validation_decision=validation_result.decision,
                        validation_reason=validation_result.reason,
                    )
                )
                if validation_result.decision != "accepted":
                    panel.validation_status = validation_result.decision
                    panel.validation_failure_reason = validation_result.reason
                    last_error = ProviderGenerationError(validation_result.reason or "single-panel validation rejected image")
                    continue
                rendered_panels.append((panel, image))
                panel.generation_succeeded = True
                panel.validation_status = "accepted"
                panel.validation_failure_reason = None
                panel.accepted_attempt_number = attempt + 1
                last_error = None
                accepted = True
                break
            except Exception as exc:  # pragma: no cover
                panel.attempt_traces.append(
                    PanelAttemptRecord(
                        attempt_number=attempt + 1,
                        strategy_name=strategy.name,
                        generated_image_available=False,
                        validation_decision="failed_generation",
                        validation_reason=str(exc),
                    )
                )
                last_error = exc
        panel.final_image_prompt = original_prompt
        panel_attempt_traces.append(_build_panel_attempt_trace(panel, accepted))
        if last_error is not None:  # pragma: no cover
            failure_message = f"Image generation failed for panel {panel.index}: {last_error}"
            panel.generation_succeeded = False
            panel.failure_message = str(last_error)
            break

    if failure_message is not None:
        panel_paths = save_panel_images(request.output_dir, rendered_panels) if rendered_panels else []
        failure_metadata = MetadataRecord(
            request=request,
            character_bible=character_bible,
            style_bible=style_bible,
            story=story,
            planner_run=planner_run,
            provider=provider.name,
            provider_mode=provider.mode,
            provider_run=ProviderRunRecord(
                provider_name=provider.name,
                provider_mode=provider.mode,
                started_with_valid_config=True,
                completed_successfully=False,
                failure_message=failure_message,
            ),
            reference_image_path=str(request.reference_image_path) if request.reference_image_path else None,
            panel_image_paths=[str(path) for path in panel_paths],
            final_comic_path="",
            panel_attempt_traces=panel_attempt_traces,
            warnings=request_warnings,
        )
        write_metadata(request.output_dir, failure_metadata)
        raise ProviderGenerationError(failure_message)

    panel_paths = save_panel_images(request.output_dir, rendered_panels)
    final_comic_path = save_final_comic(request.output_dir, compose_final_comic(panel_paths))
    metadata = MetadataRecord(
        request=request,
        character_bible=character_bible,
        style_bible=style_bible,
        story=story,
        planner_run=planner_run,
        provider=provider.name,
        provider_mode=provider.mode,
        provider_run=ProviderRunRecord(
            provider_name=provider.name,
            provider_mode=provider.mode,
            started_with_valid_config=True,
            completed_successfully=True,
        ),
        reference_image_path=str(request.reference_image_path) if request.reference_image_path else None,
        panel_image_paths=[str(path) for path in panel_paths],
        final_comic_path=str(final_comic_path),
        panel_attempt_traces=panel_attempt_traces,
        warnings=request_warnings,
    )
    metadata_path = write_metadata(request.output_dir, metadata)
    build_artifact_set(panel_paths, final_comic_path, metadata_path)
    return metadata


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "generate":
        parser.error("Unknown command")
    try:
        request = parse_request(args)
        run_generation(request)
    except (ValueError, SafetyError, ProviderConfigurationError, ProviderGenerationError) as exc:
        print(str(exc))
        return 1
    return 0


def build_provider(provider_name: str) -> ImageProvider:
    try:
        return PROVIDER_FACTORIES[provider_name]()
    except KeyError as exc:
        raise ValueError(f"Unsupported provider: {provider_name}") from exc


def _build_panel_attempt_trace(panel, accepted: bool) -> PanelAttemptTraceRecord:
    final_status = "accepted" if accepted else "failed_validation"
    failure_reason = None if accepted else panel.validation_failure_reason or panel.failure_message
    if not accepted and panel.attempt_traces and all(
        attempt.validation_decision == "failed_generation" for attempt in panel.attempt_traces
    ):
        final_status = "failed_generation"
    return PanelAttemptTraceRecord(
        panel_index=panel.index,
        final_status=final_status,
        attempts=[attempt.to_dict() for attempt in panel.attempt_traces],
        accepted_attempt_number=panel.accepted_attempt_number,
        failure_reason=failure_reason,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
