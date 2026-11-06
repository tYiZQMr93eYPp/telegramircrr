from indexers.base import BaseIndexer, indexer_class

MESSAGE = (
    "name: [Some.Release.2026.1080p]\n"
    "category: [Movies]\n"
    "size: [13.37 GiB]\n"
    "uploader: [Uploader]\n"
    "resolution: [1080p]\n"
    "freeleech: [100%]\n"
    "id: [42]\n"
    "double_upload: [true]\n"
    "refundable: [false]\n"
    "internal: [true]\n"
    "featured: [false]\n"
    "personal_release: [false]\n"
    "tmdb_id: [1]\n"
    "imdb_id: [2]\n"
    "tvdb_id: [3]\n"
    "details_link: [https://x/torrents/42]"
)


def test_parses_template(make_event):
    data = indexer_class("NOBS").parse_event(make_event(text=MESSAGE))

    assert (data.title, data.category, data.size) == ("Some.Release.2026.1080p", "Movies", "13.37 GiB")
    assert (data.uploader, data.resolution) == ("Uploader", "1080p")
    assert (data.id, data.base_url, data.freeleech) == ("42", "https://x/torrents/42", 100)
    assert (data.tmdb_id, data.imdb_id, data.tvdb_id) == ("1", "2", "3")
    assert data.tags == "double_upload,internal"
    assert data.missing_fields() == []


def test_unrecognized_message_reports_missing_fields(make_event):
    data = indexer_class("NOBS").parse_event(make_event(text="Title"))

    assert data.missing_fields() == ["title", "category", "size", "id", "base_url"]


def test_indexer_class_is_named_and_cached():
    cls = indexer_class("MyIndexer")

    assert cls.__name__ == "MyIndexer" and issubclass(cls, BaseIndexer)
    assert indexer_class("MyIndexer") is cls
