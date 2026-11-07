from indexers.base import BaseIndexer, indexer_class
from indexers.torrentland import TORRENTLAND

MESSAGE = (
    "Some.Release.2026.1080p.WEB-DL-GRP\n"
    "📺 Series -> HD\n"
    "💾 13.37 GiB\n"
    "👤 Uploader\n"
    "🔥 50 %\n"
    "Doble Subida Destacado\n"
    "[Ficha](https://tracker.example.org/torrents/18741)"
)


def test_custom_class_wins_over_the_standard_template():
    assert indexer_class("TORRENTLAND") is TORRENTLAND
    assert issubclass(TORRENTLAND, BaseIndexer)


def test_parses_torrentland_message(make_event):
    data = TORRENTLAND.parse_event(make_event(text=MESSAGE))

    assert (data.title, data.category, data.size, data.uploader) == (
        "Some.Release.2026.1080p.WEB-DL-GRP", "Series", "13.37 GiB", "Uploader")
    assert (data.id, data.base_url, data.freeleech) == ("18741", "https://tracker.example.org/torrents/18741", 50)
    assert data.tags == "double_upload,featured"
    assert data.resolution == ""
    assert data.missing_fields() == []


def test_missing_required_fields_are_still_reported(make_event):
    data = TORRENTLAND.parse_event(make_event(text="Title"))

    assert data.missing_fields() == ["category", "size", "id", "base_url"]
