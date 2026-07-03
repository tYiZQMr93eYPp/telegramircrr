import re
import unicodedata
from loguru import logger
from models.announce_data import AnnounceData
from telethon import events


_FIELDS = {
    "title": r"^(.+?)\n",
    "category": r"📺\s?(.+?)\s",
    "size": r"💾\s?(.+?)\n",
    "uploader": r"👤\s?(.+?)\n",
    "freeleech": r"(\d+)%",
    "base_url": r"\[Ficha\]\((https?://.+?)\)",
    "id": r"/torrents/(\d+?)\)",
    "double_upload": r"(Doble Subida)",
    "featured": r"(Destacado)",
    # Torrentland doesn't announce the `Refundable` value
}


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None

class Torrentland:
    @staticmethod
    def parse_event(event: events.NewMessage.Event) -> AnnounceData:
        message: str = unicodedata.normalize('NFKC', event.message.text)
        logger.debug("Raw message: {!r}", event.message.text)
        logger.debug("Normalized message: {!r}", message)
        data = {key: _get(pat, message) for key, pat in _FIELDS.items()}
        logger.debug("Parsed fields: {}", data)

        if data["base_url"] and data["title"]:
            # Hyperlinks the torrent name to the torrent page in Telegram messages
            data["title"] = f"[{data['title']}]({data['base_url']})"
            # Overwrite the FQDN of `base_url` with a placeholder since they DON'T allow automated tools
            # By doing this, we prevent any accidental (or not so accidental) intention of automating anything there
            data["base_url"] = re.sub(r"https?://[^/]+", "https://example.org", data["base_url"])

        obj = AnnounceData(**data)
        logger.debug("Parsed data: {}", vars(obj))

        return obj
