from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from comic_agent.models.bibles import CharacterBible, StyleBible
from comic_agent.models.comic_request import ComicRequest
from comic_agent.models.panel import StoryStructure


@dataclass(slots=True)
class ProviderRunRecord:
    provider_name: str
    provider_mode: str
    started_with_valid_config: bool
    completed_successfully: bool
    failure_message: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "provider_name": self.provider_name,
            "provider_mode": self.provider_mode,
            "started_with_valid_config": self.started_with_valid_config,
            "completed_successfully": self.completed_successfully,
            "failure_message": self.failure_message,
        }


@dataclass(slots=True)
class PlannerRunRecord:
    requested_mode: str
    actual_mode: str
    fallback_triggered: bool = False
    fallback_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "requested_mode": self.requested_mode,
            "actual_mode": self.actual_mode,
            "fallback_triggered": self.fallback_triggered,
            "fallback_reason": self.fallback_reason,
        }


@dataclass(slots=True)
class PanelAttemptTraceRecord:
    panel_index: int
    final_status: str
    attempts: list[dict[str, object]]
    accepted_attempt_number: int | None = None
    failure_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "panel_index": self.panel_index,
            "final_status": self.final_status,
            "attempts": self.attempts,
            "accepted_attempt_number": self.accepted_attempt_number,
            "failure_reason": self.failure_reason,
        }


@dataclass(slots=True)
class MetadataRecord:
    request: ComicRequest
    character_bible: CharacterBible
    style_bible: StyleBible
    story: StoryStructure
    planner_run: PlannerRunRecord
    provider: str
    provider_mode: str
    provider_run: ProviderRunRecord
    reference_image_path: str | None
    panel_image_paths: list[str]
    final_comic_path: str
    panel_attempt_traces: list[PanelAttemptTraceRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "request": self.request.to_dict(),
            "character_bible": self.character_bible.to_dict(),
            "style_bible": self.style_bible.to_dict(),
            "story": self.story.to_dict(),
            "planner_run": self.planner_run.to_dict(),
            "provider": self.provider,
            "provider_mode": self.provider_mode,
            "provider_run": self.provider_run.to_dict(),
            "reference_image_path": self.reference_image_path,
            "panel_image_paths": self.panel_image_paths,
            "final_comic_path": self.final_comic_path,
            "panel_attempt_traces": [trace.to_dict() for trace in self.panel_attempt_traces],
            "warnings": self.warnings,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class ComicArtifactSet:
    panel_images: list[Path]
    final_comic: Path
    metadata: Path
