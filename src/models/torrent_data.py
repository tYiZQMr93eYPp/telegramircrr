from irc_bot.utils import irc_channel_for_tracker


class TorrentData:
    def __init__(self, torrent_name: str | None = None,
                 category: str | None = None,
                 torrent_size: str | None = None,
                 uploader: str | None = None,
                 freeleech: str | None = None,
                 base_url: str | None = None,
                 torrent_id: str | None = None,
                 double_upload: str | None = None,
                 featured: str | None = None,
                 refundable: str | None = None):
        self.torrent_name = torrent_name
        self.category = category
        self.torrent_size = torrent_size
        self.uploader = uploader
        self.freeleech = int(freeleech) if freeleech is not None else 0
        self.base_url = base_url
        self.torrent_id = torrent_id
        self.tags = ",".join(t for t, v in [
            ("double_upload", double_upload),
            ("featured", featured),
            ("refundable", refundable),
        ] if v)
    def send_data_to_irc(self, tracker, irc):
        fields = {
            "Name": self.torrent_name,
            "Category": self.category,
            "Size": self.torrent_size,
            "Uploader": self.uploader,
            "Freeleech": self.freeleech,
            "URL": self.base_url,
            "Id": self.torrent_id,
            "Tags": self.tags,
        }
        message = " | ".join(f"{k}: {v}" for k, v in fields.items())
        irc.send_message(irc_channel_for_tracker(tracker), message)
