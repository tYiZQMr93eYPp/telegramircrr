import re, requests
import unicodedata
from loguru import logger
from models.announce_data import AnnounceData
from models.indexer_api import IndexerApi
from telethon import events


_FIELDS = {
    "title": r"T.tulo:\s(.+?)(?:\n|$)",
    "category": r"Categor.a:\s#?(.+?)(?:\n|$)",
    "size": r"Tama.o:\s(.+?)(?:\n|$)",
    "uploader": r"Uploader:\s(.+?)(?:\n|$)",
    "freeleech": r"Free:\s(\d+?)(?:\s|%)",
    "base_url": r"Link:\s(.+?)(?:\n|$)",
    "double_upload": r"(Double Upload)",
    "featured": r"(Destacado)",
    # HDZero doesn't announce the `Refundable` value
}


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None

class HDZERO:
    @staticmethod
    def parse_event(event: events.NewMessage.Event, api: IndexerApi | None = None) -> AnnounceData:
        message: str = unicodedata.normalize('NFKC', event.message.text)
        logger.debug("Raw message: {!r}", event.message.text)
        logger.debug("Normalized message: {!r}", message)
        data = {key: _get(pat, message) for key, pat in _FIELDS.items()}
        logger.debug("Parsed fields: {}", data)

        if data["base_url"]:
            response = requests.head(data["base_url"], allow_redirects=True, timeout=60)
            urls = [r.headers["Location"] for r in response.history if "Location" in r.headers] + [response.url]
            base_url = next((u for u in urls if re.match(r".+?/torrents/\d+", u)), None)
            if base_url:
                data["base_url"] = base_url
                data["id"] = re.search(r"/torrents/(\d+)", base_url).group(1)

        if not data.get("id") and data["title"] and api:
            found = api.find_torrent(data["title"], data["uploader"])
            logger.debug("Torrent resolved through the API: {}", found)
            if found:
                data["id"], details_link = found
                data["base_url"] = data["base_url"] or details_link

        data["indexer"] = "HDZERO"

        obj = AnnounceData(**data, normalized_message=message)
        logger.debug("Parsed data: {}", vars(obj))

        return obj
