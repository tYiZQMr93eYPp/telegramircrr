import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

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
