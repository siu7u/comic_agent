from __future__ import annotations

from abc import ABC, abstractmethod
from PIL import Image

from comic_agent.models.panel import PanelSpec


class ProviderConfigurationError(ValueError):
    pass


class ProviderGenerationError(RuntimeError):
    pass


class ImageProvider(ABC):
    name = "ImageProvider"
    mode = "unknown"

    def validate_configuration(self) -> None:
        return None

    @abstractmethod
    def generate_panel_image(self, panel: PanelSpec) -> Image.Image:
        raise NotImplementedError
