from __future__ import annotations

from pathlib import Path
from PIL import Image


CANVAS_SIZE = (1054, 1054)
PANEL_SIZE = (512, 512)
PANEL_POSITIONS = {
    1: (10, 10),
    2: (532, 10),
    3: (10, 532),
    4: (532, 532),
}


def compose_final_comic(panel_paths: list[Path]) -> Image.Image:
    canvas = Image.new("RGB", CANVAS_SIZE, color="black")
    for index, panel_path in enumerate(panel_paths, start=1):
        panel_image = Image.open(panel_path).convert("RGB")
        canvas.paste(panel_image.resize(PANEL_SIZE), PANEL_POSITIONS[index])
    return canvas

