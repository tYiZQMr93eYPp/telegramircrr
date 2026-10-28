import re
import unicodedata
from loguru import logger
from models.announce_data import AnnounceData
from telethon import events


_FIELDS = {
    "title": r"🎬\s\**(.+?)(?:\*|\n|$)",
    "category": r"Categor.a:.*?#(.+?)(?:\n|$)",
    "size": r"Tama.o:.*?\s(.+?)(?:\n|$)",
    "uploader": r"Subido\spor:.*?#(.+?)(?:\n|$)",
    "freeleech": r"🎁.*?(\d+?)\s?%\sFree",
    "featured": r"(DESTACADO)",
    # EMUWAREZ doesn't announce the `Double Upload`, and `Refundable` values
}


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None

class EMUWAREZ:
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
                    url = getattr(getattr(button, "type", None), "url", None)
                    if url and "torrents" in url and "download" not in url:
                        data["base_url"] = url
                        data["id"] = re.search(r"/torrents/(\d+)", url).group(1)
                        break

        data["indexer"] = "EMUWAREZ"
        
        obj = AnnounceData(**data, normalized_message=message)
        logger.debug("Parsed data: {}", vars(obj))

        return obj
