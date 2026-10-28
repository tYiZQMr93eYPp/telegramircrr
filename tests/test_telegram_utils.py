from types import SimpleNamespace

from telethon.tl import types
from telethon.tl.custom import Message, MessageButton

from utils.telegram_utils import button_urls


def test_falls_back_to_raw_markup_when_buttons_unresolved(make_markup):
    # A bare Message has no client/input chat, so Telethon's `buttons` is None.
    message = Message(id=1, peer_id=types.PeerChannel(1), message="x",
                      reply_markup=make_markup("https://x/torrents/1", "https://x/torrents/download/1"))

    assert message.buttons is None
    assert button_urls(message) == ["https://x/torrents/1", "https://x/torrents/download/1"]


def test_uses_resolved_buttons(make_markup):
    markup = make_markup("https://x/torrents/2")
    resolved = [[MessageButton(None, b, None, None, 1) for b in markup.rows[0].buttons]]
    message = SimpleNamespace(id=1, buttons=resolved, reply_markup=None)

    assert button_urls(message) == ["https://x/torrents/2"]


def test_no_markup_returns_empty(make_event):
    assert button_urls(make_event().message) == []


def test_callback_only_returns_empty(make_event, make_markup):
    assert button_urls(make_event(make_markup()).message) == []
