import asyncio

from matrix_bot.utils import matrix_alias_for_indexer
from models.announce_data import AnnounceData


class TORRENTEROS:
    pass


class FakeMatrix:
    def __init__(self):
        self.sent = []

    async def send_message(self, alias, message):
        self.sent.append((alias, message))


def test_alias_is_derived_from_indexer_name():
    assert matrix_alias_for_indexer(TORRENTEROS, "matrix.org") == "#telegramircrr-torrenteros:matrix.org"


def test_announce_is_sent_to_the_indexer_room():
    data = AnnounceData(title="T", category="Movies", size="1 GB", id="1", base_url="https://x/1")
    matrix = FakeMatrix()

    asyncio.run(data.send_data_to_matrix(TORRENTEROS, matrix, "matrix.org"))

    assert matrix.sent == [("#telegramircrr-torrenteros:matrix.org", data.format_message())]
    assert "Title: [T]" in matrix.sent[0][1]
