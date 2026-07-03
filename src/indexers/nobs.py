import re
import unicodedata
from loguru import logger
from models.torrent_data import TorrentData
from telethon import events


_FIELDS = {
    "torrent_name": r"🎬\s(.+?)\n",
    "category": r"Categor.a:\s(.+?)\n",
    "torrent_size": r"Tama.o:\s(.+?)\n",
    "uploader": r"Subido por:\s(.+?)",
    # NOBS doesn't announce the `Freeleech`, `Double Upload`, `Featured`, and `Refundable` values
}


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None

class NOBS:
    @staticmethod
    def parse_event(event: events.NewMessage.Event) -> TorrentData:
        message: str = unicodedata.normalize('NFKC', event.message.message)
        logger.debug("Raw message: {!r}", event.message.message)
        logger.debug("Normalized message: {!r}", message)
        data = {key: _get(pat, message) for key, pat in _FIELDS.items()}
        logger.debug("Parsed fields: {}", data)

        if event.message.reply_markup:
            for row in event.message.reply_markup.rows:
                for button in row.buttons:
                    if getattr(button, "url", None) and "torrents" in button.url:
                        data["base_url"] = button.url
                        data["torrent_id"] = re.search(r"/torrents/(\d+)", button.url).group(1)
                        break

        obj = TorrentData(**data)
        logger.debug("Parsed data: {}", vars(obj))

        return obj
