import re
import unicodedata
from functools import cache
from importlib import import_module
from loguru import logger
from models.announce_data import AnnounceData
from telethon import events


def _get(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None


class BaseIndexer:
    # Maps each `AnnounceData` field to the regex that extracts it from the normalized message.
    FIELDS: dict[str, str] = {
        "title": r"name:\s\[(.+?)\]\n",
        "category": r"category:\s\[(.+?)\]\n",
        "size": r"size:\s\[(.+?)\]\n",
        "freeleech": r"freeleech:\s\[(.+?)%",
        "base_url": r"details_link:\s\[(.+?)\]$",
        "id": r"\nid:\s\[(.+?)\]\n",
        "tmdb_id": r"tmdb_id:\s\[(.+?)\]\n",
        "imdb_id": r"imdb_id:\s\[(.+?)\]\n",
        "tvdb_id": r"tvdb_id:\s\[(.+?)\]\n",
        "uploader": r"uploader:\s\[(.+?)\]\n",
        "resolution": r"resolution:\s\[(.+?)\]\n",
    }
    # Maps each `AnnounceData` flag to the regex whose match alone sets it.
    FLAGS: dict[str, str] = {
        "double_upload": r"double_upload:\s\[true\]\n",
        "refundable": r"refundable:\s\[true\]\n",
        "internal": r"internal:\s\[true\]\n",
        "featured": r"featured:\s\[true\]\n",
        "personal_release": r"personal_release:\s\[true\]\n",
    }

    @classmethod
    def parse_event(cls, event: events.NewMessage.Event) -> AnnounceData:
        message: str = unicodedata.normalize('NFKC', event.message.text)
        logger.debug("Raw message: {!r}", event.message.text)
        logger.debug("Normalized message: {!r}", message)
        data = {key: _get(pat, message) for key, pat in cls.FIELDS.items()}
        data |= {key: bool(re.search(pat, message)) for key, pat in cls.FLAGS.items()}
        logger.debug("Parsed fields: {}", data)

        obj = AnnounceData(**data, normalized_message=message, indexer=cls.__name__)
        logger.debug("Parsed data: {}", vars(obj))

        return obj


@cache
def indexer_class(name: str) -> type[BaseIndexer]:
    # A custom `indexers/<name>.py` defining class `<name>` wins over the standard template.
    if name.isidentifier():
        module = f"indexers.{name.lower()}"
        try:
            return getattr(import_module(module), name)
        except ModuleNotFoundError as e:
            if e.name != module:
                raise
        except AttributeError:
            pass
    # Cached so the same name always yields the same class (they're compared and stored in sets).
    return type(name, (BaseIndexer,), {})
