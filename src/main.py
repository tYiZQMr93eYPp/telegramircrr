import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from irc_bot.utils import irc_channel_for_tracker
from telethon import TelegramClient, events, custom
from irc_bot.ircbot import IRCBot
from log_config import LogConfig
from mappers.tracker_mapper import TrackerMapper
from models.torrent_data import TorrentData


load_dotenv()
LogConfig().configure()

telethon_session = Path(os.getenv("TG_SESSION_PATH", "/app/irc/telethon.session"))
api_id = int(os.getenv("TG_APP_API_ID"))
api_hash = os.getenv("TG_APP_API_HASH")
client = TelegramClient(telethon_session, api_id, api_hash)

tracker_mapper = TrackerMapper(os.getenv("TRACKER_CONFIG_PATH", "/app/irc/config.yaml"))
irc_bot = IRCBot(
    os.getenv("IRC_HOST"),
    os.getenv("IRC_NICKNAME", "irc_bot"),
    [irc_channel_for_tracker(tracker) for tracker in tracker_mapper.trackers()]
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
            tracker = tracker_mapper.get_topic(channel_id, topic_id)
            logger.debug("Topic lookup: group_id={}, topic_id={} -> {}", channel_id, topic_id, tracker)
        else:
            tracker = tracker_mapper.get(channel_id)
            logger.debug("Channel lookup: channel_id={} -> {}", channel_id, tracker)
    elif chat_id is not None:
        tracker = tracker_mapper.get_chat(chat_id)
        logger.debug("Chat lookup: chat_id={} -> {}", chat_id, tracker)
    else:
        logger.debug("No channel_id or chat_id, skipping")
        return

    if tracker is None:
        logger.debug("No tracker found for message, skipping")
        return

    logger.debug("Tracker matched: {}", tracker)
    data: TorrentData = tracker().parse_event(event)
    data.send_data_to_irc(tracker, irc_bot)


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
