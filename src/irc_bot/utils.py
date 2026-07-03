def irc_channel_for_indexer(indexer) -> str:
    return f"#{indexer.__name__.lower()}_announce"
