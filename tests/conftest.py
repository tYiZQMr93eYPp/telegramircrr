from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from telethon.tl import types


@pytest.fixture
def make_markup():
    def _make(*urls: str) -> types.ReplyInlineMarkup:
        buttons = [types.KeyboardInlineButton(text="Cb", type=types.InlineButtonTypeCallback(data=b"abc"))]
        buttons += [types.KeyboardInlineButton(text="Url", type=types.InlineButtonTypeUrl(url=u)) for u in urls]
        return types.ReplyInlineMarkup(rows=[types.KeyboardInlineButtonRow(buttons=buttons)])
    return _make


@pytest.fixture
def make_event():
    def _make(markup=None, text: str = "Title") -> SimpleNamespace:
        message = SimpleNamespace(id=1, text=text, buttons=None, reply_markup=markup,
                                  date=datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc))
        return SimpleNamespace(message=message)
    return _make
