from zoneinfo import ZoneInfo

import pytest

from models.announce_data import AnnounceData
from notifications import apprise_notifier


class FakeApprise:
    instances: list["FakeApprise"] = []
    notify_result = True

    def __init__(self):
        self.urls: list[str] = []
        self.sent: list[dict] = []
        FakeApprise.instances.append(self)

    def add(self, url):
        self.urls.append(url)
        return True

    def notify(self, **kwargs):
        self.sent.append(kwargs)
        if isinstance(FakeApprise.notify_result, Exception):
            raise FakeApprise.notify_result
        return FakeApprise.notify_result


@pytest.fixture(autouse=True)
def fake_apprise(monkeypatch):
    FakeApprise.instances = []
    FakeApprise.notify_result = True
    monkeypatch.setattr(apprise_notifier.apprise, "Apprise", FakeApprise)
    monkeypatch.setattr(apprise_notifier, "_APPRISE_URL", "apprises://host/telegramircrr?overflow=split")
    monkeypatch.setattr(apprise_notifier, "_TZ", ZoneInfo("Europe/Madrid"))


@pytest.fixture
def data():
    return AnnounceData(title=None, category="Movies", size="1 GB", id="1",
                        base_url="https://x/torrents/1", normalized_message="hello world")


def notify(data, event):
    apprise_notifier.notify_missing_fields("NOBS", data, data.missing_fields(), event)


def test_disabled_without_url(monkeypatch, data, make_event):
    monkeypatch.setattr(apprise_notifier, "_APPRISE_URL", None)

    notify(data, make_event())

    assert FakeApprise.instances == []


def test_body_contents(data, make_event, make_markup):
    notify(data, make_event(make_markup("https://x/torrents/1")))

    [sent] = FakeApprise.instances[0].sent
    body = sent["body"]
    assert sent["title"].startswith("[TelegramIRCrr] Missing fields: NOBS")
    assert "`title`" in body
    assert "hello world" in body
    assert "InlineButtonTypeUrl" in body
    assert "normalized_message" not in body
    assert "2026-10-28T13:00:00+01:00" in body  # message date (12:00 UTC) in TZ


def test_markup_section_skipped_without_markup(data, make_event):
    notify(data, make_event(None))

    assert "Reply markup" not in FakeApprise.instances[0].sent[0]["body"]


@pytest.mark.parametrize("result", [False, RuntimeError("boom")])
def test_failures_do_not_raise(data, make_event, result):
    FakeApprise.notify_result = result

    notify(data, make_event())
