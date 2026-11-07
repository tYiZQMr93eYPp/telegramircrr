from indexers.base import BaseIndexer


class TORRENTLAND(BaseIndexer):
    FIELDS = {
        "title": r"^(.+?)(?:\n|$)",
        "category": r"📺\s?(.+?)\s->",
        "size": r"💾\s?(.+?)(?:\n|$)",
        "uploader": r"👤\s?(.+?)(?:\n|$)",
        "freeleech": r"(\d+?)\s?%",
        "base_url": r"\[Ficha\]\((https?://.+?)\)",
        "id": r"/torrents/(\d+?)\)",
        # Torrentland doesn't announce the `resolution`, `tmdb_id`, `imdb_id`, and `tvdb_id` values
    }
    FLAGS = {
        "double_upload": r"Doble Subida",
        "featured": r"Destacado",
        # Torrentland doesn't announce the `refundable`, `internal`, and `personal_release` values
    }
