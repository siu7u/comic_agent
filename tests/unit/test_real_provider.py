from __future__ import annotations

from comic_agent.providers.real_provider import WANX_SINGLE_PANEL_PREAMBLE, WanxImageProvider


def test_wanx_message_prepends_single_panel_preamble(monkeypatch):
    provider = WanxImageProvider()

    class FakeMessage:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    class FakeModule:
        Message = FakeMessage

    def fake_import_module(name: str):
        if name == "dashscope.api_entities.dashscope_response":
            return FakeModule
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    message = provider._build_message("The main subject is test rabbit.")

    assert message.role == "user"
    assert message.content[0]["text"].startswith(WANX_SINGLE_PANEL_PREAMBLE)
    assert message.content[0]["text"].endswith("The main subject is test rabbit.")
    assert "只生成一张完整单格插画，只画后续提示里指定的当前这一格。" in message.content[0]["text"]
    assert "不要把它画成整页漫画、四宫格、分镜条、多格连环画或拼贴。" in message.content[0]["text"]
    assert "Do not draw a full comic page, extra panels, repeated beats, or a before-and-after sequence." in message.content[0]["text"]
    assert "Do not add text labels, captions, speech bubbles, or panel borders." in message.content[0]["text"]
