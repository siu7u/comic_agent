from __future__ import annotations

import importlib
import os
from urllib.request import urlopen

from PIL import Image

from comic_agent.models.panel import PanelSpec
from comic_agent.providers.base import ImageProvider, ProviderConfigurationError, ProviderGenerationError


DASHSCOPE_API_KEY_ENV = os.getenv("DASHSCOPE_API_KEY_ENV", "DASHSCOPE_API_KEY").strip()
DASHSCOPE_IMAGE_MODEL_ENV = os.getenv("DASHSCOPE_IMAGE_MODEL_ENV", "DASHSCOPE_IMAGE_MODEL").strip()
DASHSCOPE_IMAGE_SIZE_ENV = os.getenv("DASHSCOPE_IMAGE_SIZE_ENV", "DASHSCOPE_IMAGE_SIZE").strip()
DEFAULT_DASHSCOPE_IMAGE_MODEL = "wan2.7-image"
DEFAULT_DASHSCOPE_IMAGE_SIZE = "2K"
DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
WANX_SINGLE_PANEL_PREAMBLE = (
    "只生成一张完整单格插画，只画后续提示里指定的当前这一格。"
    "不要把它画成整页漫画、四宫格、分镜条、多格连环画或拼贴。"
    "不要补画前后剧情，不要在一张图里出现多个连续瞬间。"
    "画面必须是一个完整且不可分割的单场景。"
    "不要添加标题、对白框、气泡、标签或任何分格边框。\n"
    "Generate exactly one image for the single panel described below. "
    "Do not draw a full comic page, extra panels, repeated beats, or a before-and-after sequence. "
    "Keep the image as one undivided single scene. "
    "Do not add text labels, captions, speech bubbles, or panel borders.\n\n"
)


class WanxImageProvider(ImageProvider):
    name = "WanxImageProvider"
    mode = "real"

    def __init__(self) -> None:
        self.api_key = os.getenv(DASHSCOPE_API_KEY_ENV, "").strip()
        self.model = os.getenv(DASHSCOPE_IMAGE_MODEL_ENV, "").strip() or DEFAULT_DASHSCOPE_IMAGE_MODEL
        self.size = os.getenv(DASHSCOPE_IMAGE_SIZE_ENV, "").strip() or DEFAULT_DASHSCOPE_IMAGE_SIZE

    def validate_configuration(self) -> None:
        missing: list[str] = []
        if not self.api_key:
            missing.append(DASHSCOPE_API_KEY_ENV)
        if missing:
            missing_list = ", ".join(missing)
            raise ProviderConfigurationError(
                f"Real provider configuration is incomplete. Missing environment variables: {missing_list}"
            )

    def generate_panel_image(self, panel: PanelSpec) -> Image.Image:
        self.validate_configuration()
        try:
            message = self._build_message(panel.final_image_prompt)
            image_generation = self._load_image_generation_client()
            response = image_generation.call(
                model=self.model,
                api_key=self.api_key,
                messages=[message],
                enable_sequential=True,
                n=1,
                size=self.size,
            )
            return self._decode_image_response(response)
        except ProviderConfigurationError:
            raise
        except ProviderGenerationError:
            raise
        except Exception as exc:
            raise ProviderGenerationError(f"Real provider request failed for panel {panel.index}") from exc

    def _load_image_generation_client(self):
        try:
            dashscope_module = importlib.import_module("dashscope")
            image_generation_module = importlib.import_module("dashscope.aigc.image_generation")
        except ImportError as exc:
            raise ProviderConfigurationError(
                "Real provider dependency is unavailable. Install the 'dashscope' package before using --provider wanx."
            ) from exc
        dashscope_module.base_http_api_url = DEFAULT_DASHSCOPE_BASE_URL
        return image_generation_module.ImageGeneration

    def _build_message(self, prompt: str):
        try:
            message_module = importlib.import_module("dashscope.api_entities.dashscope_response")
        except ImportError as exc:
            raise ProviderConfigurationError(
                "Real provider dependency is unavailable. Install the 'dashscope' package before using --provider wanx."
            ) from exc
        return message_module.Message(role="user", content=[{"text": f"{WANX_SINGLE_PANEL_PREAMBLE}{prompt}"}])

    def _decode_image_response(self, response) -> Image.Image:
        status_code = _read_field(response, "status_code")
        if status_code not in (None, 200):
            code = _read_field(response, "code") or "unknown"
            message = _read_field(response, "message") or "unknown error"
            raise ProviderGenerationError(
                f"DashScope request failed with status_code={status_code}, code={code}, message={message}"
            )

        output = _read_field(response, "output")
        choices = _read_field(output, "choices") if output is not None else None
        if not choices:
            raise ProviderGenerationError("Real provider returned no image choices")

        image_url = None
        for choice in choices:
            message = _read_field(choice, "message")
            contents = _read_field(message, "content") if message is not None else None
            if not contents:
                continue
            for content in contents:
                if _read_field(content, "type") == "image":
                    image_url = _read_field(content, "image")
                    if image_url:
                        break
            if image_url:
                break
        if not image_url:
            raise ProviderGenerationError("Real provider returned unusable image data")
        try:
            with urlopen(image_url) as response_stream:
                image = Image.open(response_stream).convert("RGB")
        except Exception as exc:
            raise ProviderGenerationError("Real provider returned unreadable image data") from exc
        return image


def _read_field(value, field: str):
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(field)
    return getattr(value, field, None)
