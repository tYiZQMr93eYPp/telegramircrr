import os
import re
from irc_bot.utils import irc_channel_for_indexer


_ANNOUNCE_OVERWRITE_FQDN = os.getenv("ANNOUNCE_OVERWRITE_FQDN")
_PROTOCOL_FQDN_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*://)?[^/]+")


class AnnounceData:
    def __init__(self, title: str | None = None,
                 category: str | None = None,
                 size: str | None = None,
                 uploader: str | None = None,
                 freeleech: str | None = None,
                 base_url: str | None = None,
                 id: str | None = None,
                 double_upload: str | None = None,
                 featured: str | None = None,
                 refundable: str | None = None):
        self.title = title
        self.category = category
        self.size = size
        self.uploader = uploader
        self.freeleech = int(freeleech) if freeleech is not None else 0
        self.id = id
        self.tags = ",".join(t for t, v in [
            ("double_upload", double_upload),
            ("featured", featured),
            ("refundable", refundable),
        ] if v)

        # Q: Why do we allow overwriting the FQDN?
        #    A: When integrating `autobrr` with `Sonarr` or `Radarr` (and, perhaps, other automation tools), they may invoke the
        #       `[InfoURL](https://github.com/autobrr/autobrr/blob/04ba5ccb4bc45f7fdb3f98b343c0b74b2303fb2f/internal/domain/release.go#L50)`
        #       endpoint of the indexer.
        #       By overwriting the FQDN, we save the indexer from processing unnecessary requests, but with the possibility to invoke the
        #       `[DownloadURL](https://github.com/autobrr/autobrr/blob/04ba5ccb4bc45f7fdb3f98b343c0b74b2303fb2f/internal/domain/release.go#L51)`
        #       endpoint if necessary and [properly configured](https://github.com/autobrr/autobrr/blob/04ba5ccb4bc45f7fdb3f98b343c0b74b2303fb2f/web/src/types/Indexer.d.ts#L40).
        self.base_url = (
            _PROTOCOL_FQDN_RE.sub(lambda m: (m.group(1) or "") + _ANNOUNCE_OVERWRITE_FQDN, base_url)
            if _ANNOUNCE_OVERWRITE_FQDN and base_url
            else base_url
        )


    def send_data_to_irc(self, indexer, irc):
        fields = {
            "Title": self.title,
            "Category": self.category,
            "Size": self.size,
            "Uploader": self.uploader,
            "Freeleech": self.freeleech,
            "URL": self.base_url,
            "Id": self.id,
            "Tags": self.tags,
        }
        message = " | ".join(f"{k}: {v}" for k, v in fields.items())
        irc.send_message(irc_channel_for_indexer(indexer), message)
