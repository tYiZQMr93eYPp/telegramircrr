# Telegram to IRC Announcer

Watches configured Telegram channels for new indexer announcements, parses the messages, and forwards them to their corresponding IRC announce channels.

## How it works

1. Listens for new messages on configured Telegram channels, group topics, and chats via Telethon
2. Looks up which indexer class handles that channel
3. Parses the message into structured `AnnounceData`
4. Sends a formatted announcement to the indexer's IRC channel (e.g. `#myindexer_announce`)

## Requirements

- Python 3.14+
- A [Telegram API app](https://my.telegram.org/apps) (API ID + hash)
- An IRC server

## Configuration

### Environment variables

| Variable | Description | Mandatory | Default value | Example |
|---|---|---|---|---|
| `TG_APP_API_ID` | Telegram app API ID | true | `None` | `13371337` |
| `TG_APP_API_HASH` | Telegram app API hash | true | `None` | `oyr2i1ngqk3oc0lhac5cpn0anvuta9qk` |
| `TG_SESSION_PATH` | Path to the Telethon session file | false | `/app/irc/telethon.session` | `/app/irc/telethon.session` |
| `IRC_HOST` | IRC server hostname | true | `None` | `irc.example.org` |
| `IRC_NICKNAME` | IRC bot nickname | false | `irc_bot` | `irc_bot` |
| `INDEXER_CONFIG_PATH` | Path to the indexer config YAML | false | `/app/irc/config.yaml` | `/app/irc/config.yaml` |
| `LOG_LEVEL` | The logging level | false | `INFO` | `INFO` |
| `LOG_PATH` | The log file path | false | `None` | `/app/logs/telegramircrr.log` |
| `ANNOUNCE_OVERWRITE_FQDN` | Overwrite the [`InfoURL`](https://github.com/autobrr/autobrr/blob/04ba5ccb4bc45f7fdb3f98b343c0b74b2303fb2f/internal/domain/release.go#L50)'s FQDN | false | `None` | `tracker.example.org` |

### Indexer config (`config.yaml`)

Three sections map different Telegram source types to indexer class names:

```yaml
channel_indexers:
  # TG-CHANNEL-ID_MYINDEXER: MyIndexer
  "1234567890": MyIndexer

group_topic_indexers:
  # TG-GROUP-TOPIC-ID_MYINDEXER: MyIndexer
  "1234567890_1234": MyIndexer

chat_indexers:
  # TG-CHAT-ID_MYINDEXER: MyIndexer
  "1234567890": MyIndexer

```

The IRC channel is derived automatically from the class name: `MyIndexer` → `#myindexer_announce`.

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
      INDEXER_CONFIG_PATH: #optional
      LOG_LEVEL: #optional
      LOG_PATH: #optional
      ANNOUNCE_OVERWRITE_FQDN: #optional
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
  -e INDEXER_CONFIG_PATH= `#optional` \
  -e LOG_LEVEL= `#optional` \
  -e LOG_PATH= `#optional` \
  -e ANNOUNCE_OVERWRITE_FQDN= `#optional` \
  -v /path/to/tg_announcer_config:/app/irc \
  -v /path/to/log_path:/app/logs/app.log `#optional` \
  tYiZQMr93eYPp/telegramircrr:latest
```

## Included indexers

| Indexer List |
|---|
| `HDZero` |
| `EMUWAREZ` |
| `NOBS` |
| `Torrentland` |
| `ParabellumHD` |
| `Milnueve` |

## Want to add your indexer?

1. Open an [issue](https://github.com/tYiZQMr93eYPp/telegramircrr/issues/new?template=indexer-integration-request.md) using the [Indexer Integration Request template](https://github.com/tYiZQMr93eYPp/telegramircrr/issues/new?template=indexer-integration-request.md).
2. Follow the instructions in it.
3. Submit the issue.

## Project structure

```
src/
  main.py              # Entry point
  indexers/            # One file per indexer, filename = class name lowercase
    myindexer.py
  models/
    announce_data.py    # Parsed announce data + IRC send logic
  irc_bot/
    ircbot.py          # IRC bot wrapper
    utils.py           # IRC channel name helper
  mappers/
    indexer_mapper.py  # Loads channel → indexer mapping from config.yaml
config.yaml            # Indexer mappings
```
