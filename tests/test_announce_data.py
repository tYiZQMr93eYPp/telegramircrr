import pytest

from models import announce_data
from models.announce_data import AnnounceData

COMPLETE = dict(title="T", category="Movies", size="1 GB", id="1", base_url="https://x/torrents/1")


def test_complete_data_has_no_missing_fields():
    assert AnnounceData(**COMPLETE).missing_fields() == []


@pytest.mark.parametrize("field", ["title", "category", "size", "id", "base_url"])
@pytest.mark.parametrize("empty", [None, ""])
def test_each_required_field_is_reported(field, empty):
    assert AnnounceData(**{**COMPLETE, field: empty}).missing_fields() == [field]


def test_optional_fields_are_not_required():
    data = AnnounceData(**COMPLETE, uploader=None, freeleech=None)

    assert data.missing_fields() == []


def test_missing_title_is_still_detected_when_appending_indexer(monkeypatch):
    monkeypatch.setattr(announce_data, "_APPEND_INDEXER_NAME_TO_ANNOUNCE_TITLE", True)

    assert AnnounceData(**{**COMPLETE, "title": None}, indexer="NOBS").missing_fields() == ["title"]
    assert AnnounceData(**COMPLETE, indexer="NOBS").title == "T (Indexer: NOBS)"
