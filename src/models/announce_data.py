from irc_bot.utils import irc_channel_for_indexer


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
        self.base_url = base_url
        self.id = id
        self.tags = ",".join(t for t, v in [
            ("double_upload", double_upload),
            ("featured", featured),
            ("refundable", refundable),
        ] if v)
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
