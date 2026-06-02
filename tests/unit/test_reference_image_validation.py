from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from comic_agent.cli.generate import validate_reference_image


def test_validate_reference_image_accepts_supported_file(tmp_path):
    image_path = tmp_path / "ref.png"
    Image.new("RGB", (8, 8), color="red").save(image_path)

    resolved = validate_reference_image(str(image_path))

    assert resolved == image_path


def test_validate_reference_image_rejects_missing_file(tmp_path):
    missing = tmp_path / "missing.png"

    with pytest.raises(ValueError, match="cannot be read"):
        validate_reference_image(str(missing))


def test_validate_reference_image_rejects_unsupported_type(tmp_path):
    file_path = tmp_path / "ref.txt"
    file_path.write_text("not an image", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported reference image type"):
        validate_reference_image(str(file_path))

