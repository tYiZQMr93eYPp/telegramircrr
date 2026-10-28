import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from irc_bot.utils import irc_channel_for_indexer
from telethon import TelegramClient, events, custom
from irc_bot.ircbot import IRCBot
from log_config import LogConfig
from mappers.indexer_mapper import IndexerMapper
from models.announce_data import AnnounceData
from notifications.apprise_notifier import notify_missing_fields


load_dotenv()
LogConfig().configure()

telethon_session = Path(os.getenv("TG_SESSION_PATH", "/app/irc/telethon.session"))
api_id = int(os.getenv("TG_APP_API_ID"))
api_hash = os.getenv("TG_APP_API_HASH")
client = TelegramClient(telethon_session, api_id, api_hash)

indexer_mapper = IndexerMapper(os.getenv("INDEXER_CONFIG_PATH", "/app/irc/config.yaml"))
irc_bot = IRCBot(
    os.getenv("IRC_HOST"),
    os.getenv("IRC_NICKNAME", "irc_bot"),
    [irc_channel_for_indexer(indexer) for indexer in indexer_mapper.indexers()]
)


@client.on(events.NewMessage)
async def read_messages(event: events.NewMessage.Event):
    message_ent: custom.Message = event.message

    channel_id: int | None = getattr(message_ent.peer_id, "channel_id", None)
    chat_id: int | None = getattr(message_ent, "chat_id", None)

    logger.debug("New message | peer_id={} | channel_id={} | chat_id={} | msg_id={}", message_ent.peer_id, channel_id, chat_id, message_ent.id)

    if channel_id is not None:
        reply_to = message_ent.reply_to
        is_topic = reply_to is not None and getattr(reply_to, "forum_topic", False)

        if is_topic:
            topic_id: int = reply_to.reply_to_top_id or reply_to.reply_to_msg_id
            indexer = indexer_mapper.get_topic(channel_id, topic_id)
            logger.debug("Topic lookup: group_id={}, topic_id={} -> {}", channel_id, topic_id, indexer)
        else:
            indexer = indexer_mapper.get(channel_id)
            logger.debug("Channel lookup: channel_id={} -> {}", channel_id, indexer)
    elif chat_id is not None:
        indexer = indexer_mapper.get_chat(chat_id)
        logger.debug("Chat lookup: chat_id={} -> {}", chat_id, indexer)
    else:
        logger.debug("No channel_id or chat_id, skipping")
        return

    if indexer is None:
        logger.debug("No indexer found for message, skipping")
        return

    logger.debug("Indexer matched: {}", indexer)
    logger.debug("reply_markup | indexer={} | msg_id={} | {}", indexer.__name__, message_ent.id,
                message_ent.reply_markup.to_dict() if message_ent.reply_markup else None)
    api = indexer_mapper.api(indexer)
    parse_event = indexer().parse_event
    # parse_event does HTTP call blocking, so it runs off the event loop
    if api:
        data: AnnounceData = await asyncio.to_thread(parse_event, event, api=api)
    else:
        data = await asyncio.to_thread(parse_event, event)

    missing = data.missing_fields()
    if missing:
        logger.error("Missing fields {} | indexer={} | msg_id={}", missing, indexer.__name__, message_ent.id)
        await asyncio.to_thread(notify_missing_fields, indexer.__name__, data, missing, event)

    data.send_data_to_irc(indexer, irc_bot)


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
