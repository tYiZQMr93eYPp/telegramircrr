def irc_channel_for_tracker(tracker) -> str:
    return f"#{tracker.__name__.lower()}_announce"
