from __future__ import annotations

import argparse

import pytest
from PIL import Image

from comic_agent.cli.generate import parse_request
from comic_agent.providers.base import ProviderConfigurationError
from comic_agent.providers.real_provider import DEFAULT_DASHSCOPE_IMAGE_MODEL, WanxImageProvider


def test_wanx_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    provider = WanxImageProvider()

    with pytest.raises(ProviderConfigurationError, match="DASHSCOPE_API_KEY"):
        provider.validate_configuration()


def test_wanx_provider_uses_default_model(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.delenv("DASHSCOPE_IMAGE_MODEL", raising=False)

    provider = WanxImageProvider()

    assert provider.model == DEFAULT_DASHSCOPE_IMAGE_MODEL


def test_parse_request_preserves_reference_image_for_real_provider(tmp_path):
    image_path = tmp_path / "reference.png"
    Image.new("RGB", (8, 8), color="green").save(image_path)
    args = argparse.Namespace(
        theme="A heron maps a river",
        provider="wanx",
        style=None,
        character=None,
        image_prompt=None,
        panel_prompt_1=None,
        panel_prompt_2=None,
        panel_prompt_3=None,
        panel_prompt_4=None,
        reference_image=str(image_path),
        lang="zh",
        out=str(tmp_path / "out"),
    )

    request = parse_request(args)

    assert request.provider == "wanx"
    assert request.reference_image_path == image_path
