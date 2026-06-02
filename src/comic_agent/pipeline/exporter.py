from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from PIL import Image

from comic_agent.models.metadata import ComicArtifactSet, MetadataRecord
from comic_agent.models.panel import PanelSpec


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def default_output_dir(base: Path | None = None) -> Path:
    root = (base or Path.cwd()) / "output"
    stamp = datetime.now(timezone.utc).strftime("comic-output-%Y%m%d-%H%M%S")
    return root / stamp


def save_panel_images(output_dir: Path, panels: Iterable[tuple[PanelSpec, Image.Image]]) -> list[Path]:
    paths: list[Path] = []
    for panel, image in panels:
        path = output_dir / f"panel-{panel.index}.png"
        image.save(path, format="PNG")
        panel.image_path = path
        paths.append(path)
    return paths


def save_final_comic(output_dir: Path, image: Image.Image) -> Path:
    path = output_dir / "comic.png"
    image.save(path, format="PNG")
    return path


def write_metadata(output_dir: Path, record: MetadataRecord) -> Path:
    path = output_dir / "metadata.json"
    record.created_at = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(record.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_artifact_set(panel_paths: list[Path], final_comic: Path, metadata_path: Path) -> ComicArtifactSet:
    return ComicArtifactSet(panel_images=panel_paths, final_comic=final_comic, metadata=metadata_path)
