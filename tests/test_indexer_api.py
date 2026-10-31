import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import requests

from models import indexer_api
from models.indexer_api import IndexerApi
from models.torrent import Torrent

SAMPLE = Path(__file__).parent.parent / "examples" / "unit3d-api" / "api-torrents-filter.sample1.json"


def _response(body):
    return SimpleNamespace(raise_for_status=lambda: None, json=lambda: body)


def test_find_torrent_deserializes_the_whole_match(monkeypatch):
    body = json.loads(SAMPLE.read_text())
    monkeypatch.setattr(indexer_api.requests, "get", lambda *args, **kwargs: _response(body))

    api = IndexerApi("https://tracker.example.org", "key")
    found = api.find_torrent(body["data"][0]["attributes"]["name"])

    assert isinstance(found, Torrent)
    assert found.id == "1"
    assert found.attributes.name == "The Sopranos (1999) - S01 - Pilot [WEBDL-1080p][AC3 5.1][x264]"
    assert found.attributes.tmdb_id == 1398
    assert found.attributes.created_at == datetime(2026, 10, 27, 2, 17, 32, tzinfo=timezone.utc)


def test_find_torrent_retries_transient_errors(monkeypatch):
    body = json.loads(SAMPLE.read_text())
    attempts = 0

    def get(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts < indexer_api._MAX_ATTEMPTS:
            raise requests.ConnectionError("temporary failure")
        return _response(body)

    monkeypatch.setattr(indexer_api.requests, "get", get)
    monkeypatch.setattr(indexer_api.time, "sleep", lambda _: None)

    api = IndexerApi("https://tracker.example.org", "key")
    found = api.find_torrent(body["data"][0]["attributes"]["name"])

    assert found is not None
    assert attempts == indexer_api._MAX_ATTEMPTS


def test_find_torrent_gives_up_after_max_attempts(monkeypatch):
    attempts = 0
    delays = []

    def get(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        raise requests.ConnectionError("temporary failure")

    monkeypatch.setattr(indexer_api.requests, "get", get)
    monkeypatch.setattr(indexer_api.time, "sleep", delays.append)

    api = IndexerApi("https://tracker.example.org", "key")

    assert api.find_torrent("Title") is None
    assert attempts == indexer_api._MAX_ATTEMPTS
    assert delays == [1.0, 2.0]


def test_find_torrent_does_not_retry_client_errors(monkeypatch):
    attempts = 0
    response = SimpleNamespace(status_code=404)

    def raise_for_status():
        raise requests.HTTPError(response=response)

    def get(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        return SimpleNamespace(raise_for_status=raise_for_status, json=lambda: {})

    monkeypatch.setattr(indexer_api.requests, "get", get)
    monkeypatch.setattr(indexer_api.time, "sleep", lambda _: None)

    api = IndexerApi("https://tracker.example.org", "key")

    assert api.find_torrent("Title") is None
    assert attempts == 1
