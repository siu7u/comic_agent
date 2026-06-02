from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PanelAttemptRecord:
    attempt_number: int
    strategy_name: str
    generated_image_available: bool
    validation_decision: str
    validation_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_number": self.attempt_number,
            "strategy_name": self.strategy_name,
            "generated_image_available": self.generated_image_available,
            "validation_decision": self.validation_decision,
            "validation_reason": self.validation_reason,
        }


@dataclass(slots=True)
class PanelSpec:
    index: int
    caption: str
    dialogue: str
    scene_description: str
    action: str
    emotion: str
    camera_framing: str
    visual_description: str
    generated_prompt_base: str
    final_image_prompt: str
    prompt_source: str
    warnings: list[str] = field(default_factory=list)
    retry_count: int = 0
    image_path: Path | None = None
    input_mode: str = "text_only"
    provider_name: str = ""
    provider_mode: str = "mock"
    generation_succeeded: bool = False
    failure_message: str | None = None
    accepted_attempt_number: int | None = None
    validation_status: str = "pending"
    validation_failure_reason: str | None = None
    attempt_traces: list[PanelAttemptRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "caption": self.caption,
            "dialogue": self.dialogue,
            "scene_description": self.scene_description,
            "action": self.action,
            "emotion": self.emotion,
            "camera_framing": self.camera_framing,
            "visual_description": self.visual_description,
            "generated_prompt_base": self.generated_prompt_base,
            "final_image_prompt": self.final_image_prompt,
            "prompt_source": self.prompt_source,
            "warnings": self.warnings,
            "retry_count": self.retry_count,
            "image_path": str(self.image_path) if self.image_path else None,
            "input_mode": self.input_mode,
            "provider_name": self.provider_name,
            "provider_mode": self.provider_mode,
            "generation_succeeded": self.generation_succeeded,
            "failure_message": self.failure_message,
            "accepted_attempt_number": self.accepted_attempt_number,
            "validation_status": self.validation_status,
            "validation_failure_reason": self.validation_failure_reason,
            "attempt_traces": [attempt.to_dict() for attempt in self.attempt_traces],
        }


@dataclass(slots=True)
class StoryStructure:
    title: str
    premise: str
    panels: list[PanelSpec]
    subject: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "premise": self.premise,
            "panels": [panel.to_dict() for panel in self.panels],
            "subject": self.subject,
        }
