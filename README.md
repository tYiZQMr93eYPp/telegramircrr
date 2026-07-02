# Telegram to IRC Announcer

Watches configured Telegram channels for new torrent announcements, parses the messages, and forwards them to their corresponding IRC announce channels.

## How it works

1. Listens for new messages on configured Telegram channels, group topics, and chats via Telethon
2. Looks up which tracker class handles that channel
3. Parses the message into structured `TorrentData`
4. Sends a formatted announcement to the tracker's IRC channel (e.g. `#mytracker_announce`)

## Requirements

- Python 3.14+
- A [Telegram API app](https://my.telegram.org/apps) (API ID + hash)
- An IRC server

## Configuration

### Environment variables

| Variable | Description | Mandatory | Default value |
|---|---|---|---|
| `TG_APP_API_ID` | Telegram app API ID | true | None |
| `TG_APP_API_HASH` | Telegram app API hash | true | None |
| `TG_SESSION_PATH` | Path to the Telethon session file | false | `/app/irc/telethon.session` |
| `IRC_HOST` | IRC server hostname | true | None |
| `IRC_NICKNAME` | IRC bot nickname | false | `irc_bot` |
| `TRACKER_CONFIG_PATH` | Path to the tracker config YAML | false | `/app/irc/config.yaml` |
| `LOG_LEVEL` | The logging level | false | `INFO` |
| `LOG_PATH` | The log file path | false | None |

### Tracker config (`config.yaml`)

Three sections map different Telegram source types to tracker class names:

```yaml
# Channels
channel_trackers:
  1234567890: MyTracker

# Group/forum topics. Key format: "groupID_topicID"
group_topic_trackers:
  "1234567890_1": MyTracker

# Chats
chat_trackers:
  1234567890: MyTracker
```

The IRC channel is derived automatically from the class name: `MyTracker` → `#mytracker_announce`.

## Running with Docker

> [!IMPORTANT]
> Place `config.yaml` and `telethon.session` in the named volume before starting, or authenticate locally first.

> [!IMPORTANT]
> On first run, Telethon will prompt for your phone number to authenticate.  
> The session is saved to `TG_SESSION_PATH`.

### Docker Compose (recommended)

```yaml
---
services:
  telegramircrr:
    image: tYiZQMr93eYPp/telegramircrr:latest
    container_name: telegramircrr
    environment:
      TZ: #optional
      TG_APP_API_ID: 
      TG_APP_API_HASH: 
      IRC_HOST: 
      TG_SESSION_PATH: #optional
      IRC_NICKNAME: #optional
      TRACKER_CONFIG_PATH: #optional
      LOG_LEVEL: #optional
      LOG_PATH: #optional
    volumes:
      - /path/to/tg_announcer_config:/app/irc
      - /path/to/log_path:/app/logs/app.log # optional
    restart: unless-stopped
```

### Docker CLI

```bash
docker run -d \
  --name telegramircrr \
  -e TZ= `#optional` \
  -e TG_APP_API_ID= \
  -e TG_APP_API_HASH= \
  -e IRC_HOST= \
  -e TG_SESSION_PATH= `#optional` \
  -e IRC_NICKNAME= `#optional` \
  -e TRACKER_CONFIG_PATH= `#optional` \
  -e LOG_LEVEL= `#optional` \
  -e LOG_PATH= `#optional` \
  -v /path/to/tg_announcer_config:/app/irc \
  -v /path/to/log_path:/app/logs/app.log `#optional` \
  tYiZQMr93eYPp/telegramircrr:latest
```

## Included trackers

| Tracker List |
|---|
| `HDZero` |
| `EMUWAREZ` |
| `NOBS` |

## Want to add your tracker?

1. Open an [issue](https://github.com/tYiZQMr93eYPp/telegramircrr/issues/new?template=indexer-integration-request.md) using the [Tracker Integration Request template](https://github.com/tYiZQMr93eYPp/telegramircrr/issues/new?template=indexer-integration-request.md).
2. Follow the instructions in it.
3. Submit the issue.

## Project structure

```
src/
  main.py              # Entry point
  trackers/            # One file per tracker, filename = class name lowercase
    mytracker.py
  models/
    torrent_data.py    # Parsed torrent data + IRC send logic
  irc_bot/
    ircbot.py          # IRC bot wrapper
    utils.py           # IRC channel name helper
  mappers/
    tracker_mapper.py  # Loads channel → tracker mapping from config.yaml
config.yaml            # Tracker mappings
```
