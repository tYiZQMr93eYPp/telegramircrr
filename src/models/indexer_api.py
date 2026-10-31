import threading
import time
from collections import deque
from dataclasses import dataclass, field

import requests
from loguru import logger
from pydantic import ValidationError
from models.torrent import Torrent

DEFAULT_RATE_LIMIT = 15  # lookups per minute
_RATE_WINDOW = 60.0  # seconds


@dataclass(frozen=True)
class IndexerApi:
    """Access to an indexer's `/api/torrents/filter` endpoint (UNIT3D)."""

    url: str  # scheme + fqdn, e.g. `https://tracker.example.org`
    api_key: str
    rate_limit: int = DEFAULT_RATE_LIMIT  # max lookups per minute
    # Scheduled start time of the last `rate_limit` lookups
    _calls: deque[float] = field(default_factory=deque, init=False, repr=False, compare=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False, compare=False)

    def _wait_for_slot(self) -> None:
        """Blocks until a lookup is allowed, so at most `rate_limit` start in any `_RATE_WINDOW`."""
        with self._lock:
            now = time.monotonic()
            start = now
            if len(self._calls) == self.rate_limit:
                start = max(now, self._calls.popleft() + _RATE_WINDOW)
            self._calls.append(start)
        delay = start - now
        if delay > 0:
            logger.info("Rate limit reached for {}, delaying the lookup by {:.0f}s", self.url, delay)
            time.sleep(delay)

    def find_torrent(self, title: str, uploader: str | None = None) -> Torrent | None:
        """Returns the matching torrent named `title`, or None if it can't be determined."""
        self._wait_for_slot()
        try:
            response = requests.get(
                f"{self.url}/api/torrents/filter",
                params={"name": title.strip(), "sortField": "created_at"},
                headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as e:
            # TODO: Implement retry mechanism for errors (max. up to 3 times)
            logger.warning("Torrent lookup failed for {!r}: {}", title, e)
            return None

        results = (body.get("data") if isinstance(body, dict) else None) or []
        logger.debug("Torrent lookup for {!r} returned {} result(s)", title, len(results))
        if not results:
            return None

        match = results[0]
        if len(results) > 1 and uploader:
            wanted = uploader.strip().casefold()
            match = next(
                (r for r in results if str((r.get("attributes") or {}).get("uploader") or "").strip().casefold() == wanted),
                match,
            )

        try:
            return Torrent.model_validate(match)
        except ValidationError as e:
            logger.warning("Torrent lookup for {!r} returned an invalid match: {}", title, e)
            return None
