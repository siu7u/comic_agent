from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CharacterBible:
    summary: str
    appearance_traits: list[str] = field(default_factory=list)
    personality_notes: list[str] = field(default_factory=list)
    consistency_rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "appearance_traits": self.appearance_traits,
            "personality_notes": self.personality_notes,
            "consistency_rules": self.consistency_rules,
        }


@dataclass(slots=True)
class StyleBible:
    style_name: str
    tone: str
    composition_rules: list[str] = field(default_factory=list)
    rendering_traits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "style_name": self.style_name,
            "tone": self.tone,
            "composition_rules": self.composition_rules,
            "rendering_traits": self.rendering_traits,
        }

