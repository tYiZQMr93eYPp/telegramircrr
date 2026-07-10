import irc.bot
import irc.strings
import threading


class IRCBot:
    # TODO: Support changing the port
    # TODO: Support SSL/TLS connections
    def __init__(self, server, nickname, channels: list[str], port=6667):
        self._bot = _IRCBot(server, nickname, channels, port)
        self._thread = threading.Thread(target=self._bot.start, daemon=True)
        self._thread.start()
        self._bot.all_joined.wait()

    def send_message(self, channel, message):
        self._bot.connection.privmsg(channel, message)

    def disconnect(self):
        self._bot.disconnect()

    def wait(self):
        self._thread.join()


class _IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, nickname, channels: list[str], port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channels_to_join = [irc.strings.lower(c) for c in channels]
        self._joined = set()
        self.all_joined = threading.Event()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel in self.channels_to_join:
            c.join(channel)

    def on_join(self, c, e):
        self._joined.add(irc.strings.lower(e.target))
        if self._joined >= set(self.channels_to_join):
            self.all_joined.set()
