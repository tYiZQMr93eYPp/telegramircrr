from loguru import logger
from nio import AsyncClient, JoinError


class MatrixBot:
    # Encrypted rooms (E2EE) are not supported
    def __init__(self, homeserver: str, user_id: str, access_token: str):
        self._client = AsyncClient(homeserver, user_id)
        self._client.access_token = access_token
        self._room_ids: dict[str, str] = {}

    async def join_rooms(self, aliases: list[str]):
        for alias in aliases:
            response = await self._client.join(alias)
            if isinstance(response, JoinError):
                logger.error("Could not join Matrix room {}: {}", alias, response.message)
                continue
            self._room_ids[alias] = response.room_id
            logger.info("Joined Matrix room {} ({})", alias, response.room_id)

    async def send_message(self, alias: str, message: str):
        room_id = self._room_ids.get(alias)
        if room_id is None:
            logger.warning("Not joined to Matrix room {}, skipping", alias)
            return
        response = await self._client.room_send(
            room_id,
            "m.room.message",
            {"msgtype": "m.notice", "body": message},
        )
        if not hasattr(response, "event_id"):
            logger.error("Could not send to Matrix room {}: {}", alias, response)

    async def close(self):
        await self._client.close()
