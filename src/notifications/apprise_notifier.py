import json
import os
from datetime import datetime, timezone, tzinfo
from zoneinfo import ZoneInfo

import apprise
from loguru import logger
from telethon import events

from models.announce_data import AnnounceData


def _resolve_tz() -> tzinfo:
    name = os.getenv("TZ")
    if not name:
        return timezone.utc
    try:
        return ZoneInfo(name)
    except Exception:
        logger.warning("Invalid TZ {!r}, using UTC for notification timestamps", name)
        return timezone.utc


def _resolve_url() -> str | None:
    url = os.getenv("APPRISE_URL")
    if not url:
        return None
    if "overflow=" not in url:
        url += ("&" if "?" in url else "?") + "overflow=split"
    return url


_TZ = _resolve_tz()
_APPRISE_URL = _resolve_url()


def _format_time(value: datetime | None) -> str | None:
    return value.astimezone(_TZ).isoformat(timespec="seconds") if value else None


def _fence(content: str, lang: str = "") -> str:
    # Keep the payload from closing the fence early.
    return "```{}\n{}\n```".format(lang, content.replace("```", "'''"))


def notify_missing_fields(indexer_name: str, data: AnnounceData, missing: list[str],
                          event: events.NewMessage.Event) -> None:
    if not _APPRISE_URL:
        return

    try:
        fields = {k: v for k, v in vars(data).items() if k != "normalized_message"}
        # The first body line starts with a zero-width space (U+200B) to add spacing after the title in Telegram.
        sections = [
            "​\n**Missing fields:** {}".format(", ".join("`{}`".format(m) for m in missing)),
            "**Message date:** `{}`".format(_format_time(event.message.date)),
            "**Processed at:** `{}`".format(_format_time(datetime.now(timezone.utc))),
            "**AnnounceData**\n" + _fence(json.dumps(fields, ensure_ascii=False, indent=2, default=str), "json"),
            "**Normalized message**\n" + _fence(data.normalized_message or ""),
        ]
        markup = getattr(event.message, "reply_markup", None)
        if markup is not None and hasattr(markup, "to_dict"):
            sections.append("**Reply markup**\n" + _fence(json.dumps(markup.to_dict(), ensure_ascii=False, indent=2, default=str), "json"))

        notifier = apprise.Apprise()
        if not notifier.add(_APPRISE_URL):
            logger.error("Invalid APPRISE_URL, notification skipped")
            return
        sent = notifier.notify(
            title="[TelegramIRCrr] Missing fields: {}\n".format(indexer_name),
            body="\n\n".join(sections),
            body_format=apprise.NotifyFormat.MARKDOWN,
        )
        if not sent:
            logger.error("Apprise notification failed for indexer {}", indexer_name)
    except Exception:
        logger.exception("Apprise notification raised for indexer {}", indexer_name)
