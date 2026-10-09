import re
import unicodedata
from loguru import logger
from models.announce_data import AnnounceData
from telethon import events


_FIELDS = {
    "title": r"\*\*\n\n\*\*(.+?)\*\*\n",
    "category": r"Categor.a:\*\*\s#?(.+?)(?:\n|$)",
    "size": r"Tama.o:\*\*\s(.+?)(?:\n|$)",
    "uploader": r"Subido\spor\s#?(.+?)(?:\n|$)",
    # TORRENTEROS doesn't announce the `Double Upload`, `Freeleech`, `Featured`, and `Refundable` values
}


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None

class TORRENTEROS:
    @staticmethod
    def parse_event(event: events.NewMessage.Event) -> AnnounceData:
        message: str = unicodedata.normalize('NFKC', event.message.text)
        logger.debug("Raw message: {!r}", event.message.text)
        logger.debug("Normalized message: {!r}", message)
        data = {key: _get(pat, message) for key, pat in _FIELDS.items()}
        logger.debug("Parsed fields: {}", data)

        if event.message.reply_markup:
            for row in event.message.reply_markup.rows:
                for button in row.buttons:
                    if getattr(button, "url", None) and "torrents" in button.url and "download" not in button.url:
                        data["base_url"] = button.url
                        data["id"] = re.search(r"/torrents/(\d+)", button.url).group(1)
                        break

        # Append resolution to the title, as the indexer may announce "FULLHD" instead of "1080p".
        if data["title"]:
            resolution = re.search(r"Resoluci.n:\*\*\s#?(.+?)(?:\n|$)", message)
            data["title"] = "{} (Resolution: {})".format(data["title"], resolution.group(1) if resolution else "")

        data["indexer"] = "TORRENTEROS"

        obj = AnnounceData(**data)
        logger.debug("Parsed data: {}", vars(obj))

        return obj
