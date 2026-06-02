from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from comic_agent.models.panel import PanelSpec
from comic_agent.providers.base import ImageProvider


class MockImageProvider(ImageProvider):
    name = "MockImageProvider"
    mode = "mock"

    def generate_panel_image(self, panel: PanelSpec) -> Image.Image:
        image = Image.new("RGB", (512, 512), color="white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        lines = [
            f"Panel {panel.index}",
            panel.caption[:40],
            f"Mode: {'REF' if panel.input_mode == 'reference_guided' else 'TXT'}",
        ]
        y = 24
        for line in lines:
            draw.text((24, y), line, fill="black", font=font)
            y += 24
        draw.rectangle((10, 10, 501, 501), outline="black", width=2)
        return image
