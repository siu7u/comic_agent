from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ComicRequest:
    theme: str
    provider: str = "wanx"
    planner_mode: str | None = None
    style: str | None = None
    character: str | None = None
    image_prompt: str | None = None
    panel_prompts: dict[int, str] = field(default_factory=dict)
    reference_image_path: Path | None = None
    lang: str = "zh"
    output_dir: Path = Path("output")

    def to_dict(self) -> dict[str, object]:
        return {
            "theme": self.theme,
            "provider": self.provider,
            "planner_mode": self.planner_mode,
            "style": self.style,
            "character": self.character,
            "image_prompt": self.image_prompt,
            "panel_prompts": {str(k): v for k, v in sorted(self.panel_prompts.items())},
            "reference_image_path": str(self.reference_image_path) if self.reference_image_path else None,
            "lang": self.lang,
            "output_dir": str(self.output_dir),
        }
