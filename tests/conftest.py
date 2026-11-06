from datetime import datetime, timezone
from types import SimpleNamespace

import pytest


@pytest.fixture
def make_event():
    def _make(text: str = "Title") -> SimpleNamespace:
        message = SimpleNamespace(id=1, text=text, date=datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc))
        return SimpleNamespace(message=message)
    return _make
