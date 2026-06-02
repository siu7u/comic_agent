from __future__ import annotations

from pathlib import Path

from PIL import Image

from comic_agent.pipeline.composer import compose_final_comic


def test_layout_creates_fixed_canvas_and_places_panels(tmp_path):
    colors = ["red", "green", "blue", "yellow"]
    panel_paths: list[Path] = []
    for idx, color in enumerate(colors, start=1):
        path = tmp_path / f"panel-{idx}.png"
        Image.new("RGB", (512, 512), color=color).save(path)
        panel_paths.append(path)

    final = compose_final_comic(panel_paths)

    assert final.size == (1054, 1054)
    assert final.getpixel((20, 20)) == (255, 0, 0)
    assert final.getpixel((542, 20))[1] > 0
    assert final.getpixel((20, 542))[2] > 0
    assert final.getpixel((542, 542)) == (255, 255, 0)
    assert final.getpixel((5, 5)) == (0, 0, 0)

